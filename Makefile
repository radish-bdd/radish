all:
	echo build done


install:
	mkdir -p ${DESTDIR}/usr/lib/python2.7/dist-packages/radish
	mkdir -p ${DESTDIR}/usr/bin
	cp -r radish/* ${DESTDIR}/usr/lib/python2.7/dist-packages/radish
	cp -r bin/radish ${DESTDIR}/usr/bin/radish
