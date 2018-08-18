
all:
	$(error Please choose a test to run.)

basic:
	$(MAKE) -C tests/basic run
abstract:
	$(MAKE) -C tests/abstract run
stl:
	$(MAKE) -C tests/stl run

