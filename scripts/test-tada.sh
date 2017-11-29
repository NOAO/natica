
testfile=/data/tada-test-data/short-drop/20141220/wiyn-whirc/obj_355.fits.fz
cd /sandbox/natica/tada
#python3 tada.py --overwrite --loglevel DEBUG $testfile
af=`python3 tada.py --overwrite $testfile`

cont="&'CONTINUE  '"
val=`fitsheader $af | grep DTACQNAM | sed -e "s/$cont//" -e "s/DTACQNAM= //" -e "s/^'//" -e "s/' \+$//"`
#val=/sandbox/tada/tests/smoke/tada-test-data/short-drop/20141220/wiyn-whirc/obj_355.fits.fz
