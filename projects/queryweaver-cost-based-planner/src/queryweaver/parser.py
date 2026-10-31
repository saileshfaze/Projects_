"""Small deterministic SQL lexer/parser. Not a general SQL implementation."""
from __future__ import annotations
import re
from .model import Column, Predicate, Query, Relation

TOKEN = re.compile(r"\s*(?:(?P<number>\d+(?:\.\d+)?)|(?P<literal>'(?:''|[^'])*')|(?P<name>[A-Za-z_][A-Za-z_0-9]*)|(?P<op><=|>=|!=|<>|[=<>.,*()]))", re.ASCII)
KEYWORDS = {"SELECT", "FROM", "JOIN", "INNER", "ON", "WHERE", "AND", "LIMIT", "AS"}


class SQLSyntaxError(ValueError):
    pass


def tokenize(sql: str) -> list[str]:
    if len(sql) > 10000:
        raise SQLSyntaxError("SQL exceeds 10000 characters")
    result = []
    i = 0
    while i < len(sql):
        if sql[i:].isspace():
            break
        match = TOKEN.match(sql, i)
        if not match:
            raise SQLSyntaxError(f"Unsupported SQL at position {i}")
        result.append(match.group(match.lastgroup))
        i = match.end()
    return result


class Parser:
    def __init__(self, sql: str):
        self.tokens = tokenize(sql)
        self.pos = 0
        self.aliases: dict[str, str] = {}

    def peek(self) -> str:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ""

    def pop(self) -> str:
        if not self.peek():
            raise SQLSyntaxError("Unexpected end of SQL")
        value = self.peek()
        self.pos += 1
        return value

    def accept(self, value: str) -> bool:
        if self.peek().upper() == value:
            self.pop()
            return True
        return False

    def expect(self, value: str) -> None:
        if not self.accept(value):
            raise SQLSyntaxError(f"Expected {value}, found {self.peek()!r}")

    def ident(self) -> str:
        value = self.pop()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", value) or value.upper() in KEYWORDS:
            raise SQLSyntaxError(f"Invalid identifier: {value}")
        return value.lower()

    def column(self) -> Column:
        table = self.ident()
        self.expect(".")
        name = self.ident()
        return Column(table, name)

    def value(self) -> Column | int | float | str:
        value = self.peek()
        if value.startswith("'"):
            return self.pop()[1:-1].replace("''", "'")
        if re.fullmatch(r"\d+(?:\.\d+)?", value):
            self.pop()
            return float(value) if "." in value else int(value)
        return self.column()

    def predicate(self) -> Predicate:
        left = self.column()
        op = self.pop()
        if op not in {"=", "!=", "<>", "<", ">", "<=", ">="}:
            raise SQLSyntaxError(f"Invalid comparison operator {op}")
        return Predicate(left, "!=" if op == "<>" else op, self.value())

    def relation(self) -> Relation:
        name = self.ident()
        alias = name
        if self.accept("AS"):
            alias = self.ident()
        elif self.peek() and re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", self.peek()) and self.peek().upper() not in KEYWORDS:
            alias = self.ident()
        if alias in self.aliases:
            raise SQLSyntaxError(f"Duplicate alias: {alias}")
        self.aliases[alias] = name
        return Relation(name, alias)

    def parse(self) -> Query:
        self.expect("SELECT")
        cols = None
        if not self.accept("*"):
            result = [self.column()]
            while self.accept(","):
                result.append(self.column())
            cols = tuple(result)
        self.expect("FROM")
        relations = [self.relation()]
        joins = []
        while True:
            self.accept("INNER")
            if not self.accept("JOIN"):
                break
            relations.append(self.relation())
            self.expect("ON")
            predicate = self.predicate()
            if predicate.op != "=" or not isinstance(predicate.right, Column):
                raise SQLSyntaxError("JOIN ON requires column equality")
            joins.append(predicate)
            while self.accept("AND"):
                predicate = self.predicate()
                if predicate.op != "=" or not isinstance(predicate.right, Column):
                    raise SQLSyntaxError("JOIN ON requires column equality")
                joins.append(predicate)
        filters = []
        if self.accept("WHERE"):
            filters.append(self.predicate())
            while self.accept("AND"):
                filters.append(self.predicate())
            if any(isinstance(p.right, Column) for p in filters):
                raise SQLSyntaxError("WHERE currently supports literal comparisons only")
        limit = None
        if self.accept("LIMIT"):
            token = self.pop()
            if not token.isdigit():
                raise SQLSyntaxError("LIMIT must be an integer")
            limit = int(token)
            if limit > 100000:
                raise SQLSyntaxError("LIMIT exceeds maximum 100000")
        if self.peek():
            raise SQLSyntaxError(f"Unexpected trailing token: {self.peek()}")
        if len(relations) > 8:
            raise SQLSyntaxError("At most eight relations supported")
        aliases = {r.alias for r in relations}
        for col in (cols or ()):
            if col.table not in aliases:
                raise SQLSyntaxError(f"Unknown alias {col.table}")
        for pred in (*joins, *filters):
            for col in (pred.left, pred.right):
                if isinstance(col, Column) and col.table not in aliases:
                    raise SQLSyntaxError(f"Unknown alias {col.table}")
        for pred in joins:
            if pred.left.table == pred.right.table:
                raise SQLSyntaxError("Join predicate must connect two relations")
        return Query(cols, tuple(relations), tuple(joins), tuple(filters), limit)


def parse(sql: str) -> Query:
    return Parser(sql).parse()
