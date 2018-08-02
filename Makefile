
all:
	$(error Please choose a test to run.)

basic:
	$(MAKE) -C tests/basic

