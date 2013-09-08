Chaco - plotting library - http://code.enthought.com/chaco/

1) Chaco image plot only shows white canvas,
   problem describe at https://mail.enthought.com/pipermail/enthought-dev/2013-March/032196.html

   _agg.so is chaco library which is required to get properly generated png's files

  this library has to be copied into directory where chaco library is installed, for example:

  /usr/local/lib/python2.7/dist-packages/enable-4.3.0-py2.7-linux-x86_64.egg/kiva/agg
  /usr/local/lib/python2.7/dist-packages/kiva/agg

  [environment: linux 3.8.0-30-generic #44-Ubuntu SMP x86_64 GNU/Linux]
