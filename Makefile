
all:
	$(error Please choose a test to run.)

ifdef EPY
	RULE=epy
else
	RULE=run
endif

ifdef LIB
	RULE=library
else
	RULE=run
endif

basic:
	$(MAKE) -C tests/basic $(RULE)
abstract:
	$(MAKE) -C tests/abstract $(RULE)
stl:
	$(MAKE) -C tests/stl $(RULE)
overload:
	$(MAKE) -C tests/overload $(RULE)

