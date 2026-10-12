from decimal import Decimal
import pytest
from nimbusledger.core import allocate, anomaly_scores, summarize

def test_allocation_preserves_cents():
    result = allocate(Decimal('100.01'), {'a': Decimal('1'), 'b': Decimal('2')})
    assert sum(result.values()) == Decimal('100.01')

def test_zero_weights_rejected():
    with pytest.raises(ValueError):
        allocate(Decimal('5'), {'a': Decimal('0')})

def test_anomaly():
    assert anomaly_scores([1, 1, 1, 100])[-1] == float('inf')

def test_summary():
    assert summarize([{'service':'compute','cost':'1.25'},{'service':'compute','cost':'2.00'}])['compute'] == Decimal('3.25')
