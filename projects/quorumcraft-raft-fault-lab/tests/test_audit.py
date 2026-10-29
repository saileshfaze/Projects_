from quorumcraft.audit import AuditChain


def test_chain_valid():
    chain = AuditChain()
    chain.append(1, "test", {"x": 1})
    chain.append(2, "test", {"x": 2})
    assert chain.verify()


def test_chain_detects_modified_event():
    chain = AuditChain()
    chain.append(1, "test", {"x": 1})
    chain.records[0]["details"]["x"] = 99
    assert not chain.verify()


def test_chain_detects_reorder():
    chain = AuditChain()
    chain.append(1, "first", {})
    chain.append(2, "second", {})
    chain.records.reverse()
    assert not chain.verify()


def test_chain_detects_missing_record():
    chain = AuditChain()
    chain.append(1, "first", {})
    chain.append(2, "second", {})
    chain.records.pop(0)
    assert not chain.verify()
