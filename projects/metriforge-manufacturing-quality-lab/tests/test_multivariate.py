import pytest
from metriforge.multivariate import multivariate_scores

def test_outlier_scores_high():
    ref=[[i*.1,(i%3)*.2] for i in range(30)]
    result=multivariate_scores(ref,[[100,100],[1,1]])
    assert 0 in result['flagged_indices'] and result['scores'][0]>result['scores'][1]
def test_bad_dimensions():
    with pytest.raises(ValueError):multivariate_scores([[1,2]],[[3,4]])
def test_bad_ridge():
    with pytest.raises(ValueError):multivariate_scores([[i,i+1] for i in range(20)],[[2,3]],ridge=0)
