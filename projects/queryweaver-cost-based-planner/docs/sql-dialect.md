# Supported SQL dialect

SELECT qualified_columns_or_star FROM relation [INNER JOIN relation ON qualified_column = qualified_column [AND ...]]* [WHERE qualified_column operator literal [AND ...]] [LIMIT integer]

Identifiers use letters, digits and underscores, starting with a letter or underscore. Columns require table aliases. Literals are nonnegative numbers or single-quoted strings with doubled quote escaping. Comparisons: =, !=, <>, <, >, <=, >=. Only inner equijoins; at most eight relations; LIMIT up to 100000; SQL text up to 10000 characters.

Unsupported syntax is rejected: DELETE, UPDATE, OR, aggregates, outer joins, unqualified columns, subqueries, semicolons, column-to-column WHERE, ORDER BY, negative literals, and transactions. This parser is not a general SQL sanitizer.
