
from __future__ import absolute_import, division, print_function

import tldp.doctypes

ex_linuxdoc = {
               'ext': '.sgml',
               'type': tldp.doctypes.linuxdoc.Linuxdoc,
               'content': '''<!doctype linuxdoc system>
<article>
<title>B
<author>A
<date>2016-02-11
<abstract> abstract </abstract>
<toc>
<sect>Introduction
<p>
<sect>Stuff.
<p>
<sect>More-stuff.
<p>
</article>''',
              }

ex_docbooksgml = {
                  'ext': '.sgml',
                  'type': tldp.doctypes.docbooksgml.DocbookSGML,
                  'content': '''<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook V4.1//EN">
<article>
  <articleinfo>
    <title>T</title>
    <author>
      <firstname>A</firstname> <surname>B</surname>
      <affiliation>
        <address><email>devnull@example.org</email></address>
      </affiliation>
    </author>
    <pubdate>2016-02-11</pubdate>
    <abstract><para>abstract</para> </abstract>
    <revhistory>
       <revision>
         <revnumber>1.0</revnumber>
         <date>2016-02-11</date>
         <authorinitials>AB</authorinitials>
         <revremark>Initial release.</revremark>
       </revision>
    </revhistory>

  </articleinfo>

  <sect1 id="intro"><title>Introduction</title>
    <para>Text</para>
    <sect2 id="copyright"><title>More stuff</title>
      <para>Text</para>
    </sect2>
  </sect1>
</article>'''
                 }

ex_docbook4xml = {
                 'ext': '.xml',
                 'type': tldp.doctypes.docbook4xml.Docbook4XML,
                 'content': '''<?xml version="1.0" standalone="no"?>
<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook XML V4.1.2//EN"
                         "http://www.oasis-open.org/docbook/xml/4.2/docbookx.dtd">
<article>
  <articleinfo>
    <title>T</title>
    <author><firstname>A</firstname><surname>B</surname></author>
    <authorinitials>AB</authorinitials>
    <revhistory> <revision>
         <revnumber>v0.0</revnumber>
         <date>2016-02-11</date>
         <authorinitials>AB</authorinitials>
          <revremark> Initial release.  </revremark>
      </revision> </revhistory>
    <abstract> <para> abstract </para> </abstract>
  </articleinfo>

  <sect1 id="intro">
    <title>Intro</title>
    <para>Text</para>
    <sect2>
      <title>Intro</title>
      <para>Text</para>
    </sect2>
  </sect1>

</article>'''
                }

ex_docbook5xml = {
                 'ext': '.xml',
                 'type': tldp.doctypes.docbook5xml.Docbook5XML,
                 'content': '''<?xml version="1.0" encoding="utf-8"?>
<article xmlns="http://docbook.org/ns/docbook" version="5.0" xml:lang="en">
  <title>Sample article</title>
  <para>This is a ridiculously terse article.</para>
</article>'''
                }

ex_rst = {
          'ext': '.rst',
          'type': tldp.doctypes.rst.RestructuredText,
          'content': '''Empty.''',
         }

ex_text = {
           'ext': '.txt',
           'type': tldp.doctypes.text.Text,
           'content': '''Empty.''',
          }

ex_markdown = {
               'ext': '.md',
               'type': tldp.doctypes.markdown.Markdown,
               'content': '''Empty.''',
              }


# -- end of file
