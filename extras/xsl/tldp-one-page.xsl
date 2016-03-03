<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- TLDP One Page HTML XSL; create a single-page HTML output
     This is a small customization layer on top of upstream
     docbook-xsl-stylesheets.  Since the XML_CATALOG_FILES will locate the
     installed version of the required import resources, we will use the
     system identifier in the xsl:import line.
  -->
<xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl"/>
<xsl:import href="tldp-common.xsl"/>

<!-- This set of customizations is used to generate the entire XML
     document on a single HTML page. -->

</xsl:stylesheet>
