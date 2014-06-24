NAME=fapi
all: version build documentation 
build:
	test ! -d bin && mkdir bin || exit 0
	cp -p ./src/$(NAME) bin/$(NAME)
	sed -i "s/VERSION_DEVEL/$$(cat .version)/" bin/$(NAME)
# 'install' installes a fake-root, which will be used to build the Debian package
# $DESTDIR is actually set by the Debian tools
install:
	test ! -d $(DESTDIR)/usr/bin && mkdir -p $(DESTDIR)/usr/bin || exit 0
	test ! -d $(DESTDIR)/usr/share/$(NAME) && mkdir -p $(DESTDIR)/usr/share/$(NAME) || exit 0
	cp ./bin/$(NAME) $(DESTDIR)/usr/bin/$(NAME)
	cp $(NAME).conf.sample $(DESTDIR)/usr/share/$(NAME)
	test -z '$(DESTDIR)' && gzip -c ./docs/$(NAME).1 > /usr/share/man/man1/$(NAME).1.gz || exit 0
deinstall:
	test ! -z '$(DESTDIR)' && test -f $(DESTDIR)/usr/bin/$(NAME) && rm $(DESTDIR)/usr/bin/$(NAME) || exit 0
	test ! -z '$(DESTDIR)' && test -f $(DESTDIR)/usr/share/$(NAME) && rm -r $(DESTDIR)/usr/share/$(NAME) || exit 0
	test -z '$(DESTDIR)' && rm /usr/share/man/man1/$(NAME).1.gz
clean:
	rm bin/*
# Parses the version out of the Debian changelog
version:
	cut -d' ' -f2 debian/changelog | head -n 1 | sed 's/(//;s/)//' > .version
# Builds the documentation into a manpage
documentation:
	# To be replaced with sphynx instead of pod
	pod2man --release="$(NAME) $$(cat .version)" \
		--center="User Commands" ./docs/$(NAME).pod > ./docs/$(NAME).1
	pod2text ./docs/$(NAME).pod > ./docs/$(NAME).txt
	cp ./docs/$(NAME).pod README.pod
	./bin/fapi -h -n > ./docs/synopsis.txt
	./bin/fapi -h -n -E  > ./docs/extended-synopsis.txt
# Build a debian package 
deb: all
	dpkg-buildpackage # -us -uc
dch: 
	dch -i
release: dch deb 
	bash -c "git tag $$(cat .version)"
	git commit -a -m 'New release'
	git push origin master --tags
	git push buetoworg master --tags
clean-top:
	rm ../$(NAME)_*.tar.gz
	rm ../$(NAME)_*.dsc
	rm ../$(NAME)_*.changes
	rm ../$(NAME)_*.deb
dput:
	dput -u wheezy-buetowdotorg ../$(NAME)_$$(cat ./.version)_amd64.changes
	dput -u jessie-buetowdotorg ../$(NAME)_$$(cat ./.version)_amd64.changes
dput-debrepo:
	dput -u incoming-debrepo ../$(NAME)_$$(cat ./.version)_amd64.changes
