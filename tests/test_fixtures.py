# tests to ensure test fixtures work as expected


TEST_MESSAGE = "test_persistence_between_tests"
SENTINEL = "---EOF---"


def test_callbacks_put(callbacks):
    callbacks.put(1)
    callbacks.put(2)
    callbacks.put(3)

    i = callbacks.get()
    assert i == 1
    cbl = callbacks.list(count=2)
    assert cbl == [2, 3]
    callbacks.put(TEST_MESSAGE)


def test_callbacks_persist(callbacks):

    cb1 = callbacks.list(timeout=0.25)
    assert cb1 == [TEST_MESSAGE]
    callbacks.clear()
    cb2 = callbacks.list(block=False)
    assert cb2 == []


def test_callbacks_put_str(callbacks):
    callbacks.put("one")
    callbacks.put(SENTINEL)
    cbl = callbacks.list(sentinel=SENTINEL)
    assert isinstance(cbl, list)
    assert "one" in cbl


def test_callbacks_put_get(callbacks):
    callbacks.clear()
    assert callbacks.size() == 0
    assert callbacks.empty()
    callbacks.put("howdy")
    assert callbacks.size() == 1
    assert not callbacks.empty()
    assert callbacks.get() == "howdy"
    assert callbacks.empty()
    assert callbacks.size() == 0


def test_callbacks_list_count(callbacks):
    assert callbacks.empty()
    callbacks.put("one")
    callbacks.put("two")
    callbacks.put("three")
    cblist = callbacks.list(count=3)
    assert cblist == ["one", "two", "three"]


def test_callbacks_list_timeout(callbacks):
    assert callbacks.empty()
    callbacks.put("one")
    callbacks.put("two")
    callbacks.put("three")
    cblist = callbacks.list(timeout=0.25)
    assert cblist == ["one", "two", "three"]
