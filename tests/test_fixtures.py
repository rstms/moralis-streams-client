# tests to ensure test fixtures work as expected

def test_callbacks_put(callbacks):
    callbacks.put(1)
    callbacks.put(2)
    callbacks.put(3)

    cb = callbacks.get()
    assert cb == [1, 2, 3]

def test_callbacks_persist(callbacks):

    cb1 = callbacks.list()
    assert cb1 == [1, 2, 3]
    callbacks.clear()
    cb2 = callbacks.list()
    assert cb2 == []

def test_callbacks_put_str(callbacks):
    callbacks.put('one')
    assert 'one' in callbacks.list()

def test_callbacks_put_get(callbacks):
    callbacks.clear()
    assert callbacks.size() == 0
    assert callbacks.empty()
    callbacks.put('howdy')
    assert callbacks.size() == 1
    assert not callbacks.empty()
    assert callbacks.get() == 'howdy'
    assert callbacks.empty()
    assert callbacks.size() == 0

def test_callbacks_getlist(callbacks):
    callbacks.put('one')
    callbacks.put('two')
    callbacks.put('three')
    cblist = callbacks.list()
    assert cblist == ['one', 'two', 'three'] 

