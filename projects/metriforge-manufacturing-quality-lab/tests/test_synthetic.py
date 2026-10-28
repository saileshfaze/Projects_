from metriforge.synthetic import generate

def test_deterministic(): assert generate(seed=10)==generate(seed=10)
def test_seed_changes(): assert generate(seed=10)!=generate(seed=11)
def test_lengths():
    base,prod,labels=generate();assert len(base)==80 and len(prod)==120 and len(labels)==120
def test_labels_shift():
    _,_,labels=generate();assert labels[0]['shift']==0 and labels[-1]['shift']==1
