
all:
	$(error Please choose a test to run.)

basic:
	$(MAKE) -C tests/basic
abstract:
	$(MAKE) -C tests/abstract

