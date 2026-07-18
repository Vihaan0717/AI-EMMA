---
title: "The SLAX Scripting Language: An Alternate Syntax for XSLT"
source: http://juniper.github.io/libslax/slax-manual.html
date: 2026-06-01
tags:
  - news
  - auto-learning
  - auto-injected
---

# The SLAX Scripting Language: An Alternate Syntax for XSLT

This section includes discussion of SLAX language issues.
XPath expressions use a style of type promotion that coerces values into the particular type needed for the expression. For example, if a predicate refers to a node, then that predicate is true if the node exists. The value of the node is not considered, just it's existence.
For example, the expression "chapter[section]" selects all chapters that have a section element as a child.
Similarly, if a predicate uses a function that needs a string, the argument is converted to a string value by concatenating all the text values of that node and all that node's child elements.
For example, the expression "chapter[starts-with(section, 'A')]" will inspect all <chapter> elements, convert their <section> elements to strings, and select those whose string value starts with 'A'. This may be an expensive operation.
XSLT has immutable variables. This was done to support various optimizations and advanced streaming functionality. But it remains one of the most painful parts of XSLT. We use SLAX in JUNOS and provide the ability to perform XML-based RPCs to local and remote JUNOS boxes. One RPC allows the script to store and retrieve values in an SNMP MIB (the jnxUtility MIB). We have users using this to "fake" mutable variables, so for our environment, any theoretical arguments against the value of mutable variables are lost. They are happening, and the question becomes whether we want to force script writers into mental anguish to allow them.
Yes, exactly. That was an apologetical defense of the following code, which implements mutable variables. Dio, abbi pieta della mia anima.
The rest of this section contacts mind-numbing comments on the implementation and inner working of mutable variables.
For the typical scriptor, the important implications are:
- Non-standard feature: mutable variables are not available outside the libslax environment. This will significantly affect the portability of your scripts. Avoid mutable variables if you want to use your scripts in other XSLT implementations or without libslax.
- Memory Overhead: Due to the lifespan of XML elements and RTFs inside libxslt, mutable variables must retain copies of their previous values (when non-scalar values are used) to avoid dangling references. This means that heavy use of mutable variables will significantly affect memory overhead, until the mutable variables fall out of scope.
- Axis Implications: Since values for mutable variables are copied (see above), the operations of axes will be affected. This is a relatively minor issue, but should be noted.
Let's consider the memory issues associated with mutable variables. libxslt gives two ways to track memory WRT garbage collection:
- contexts
- as RTF/RVT (type XPATH_XSLT_TREE)
- variables
- strings (simple; forget I even mentioned them) or node sets (type XPATH_NODESET)
- via the nodesetval field
- does not track nodes, but references nodes in other trees
The key is that by having node sets refer to nodes "in situ" where they reside on other documents, the idea of refering to nodes in the input document is preserved. Node sets don't require an additional memory hook or a reference count.
The key functions here are xmlXPathNewValueTree() and xmlXPathNewNodeSet(). Both return a fresh xmlXPathObject, but xmlXPathNewValueTree will set the xmlXPathObject's "boolval" to 1, which tells xmlXPathFreeObject() to free the nodes contained in a nodeset, not just the nodeTab that holds the references.
Also note that if one of the nodes in the node set is a document (type XML_DOCUMENT_NODE) then xmlFreeDoc() is called to free the document. For RTFs, the only member of the nodeset is the root of the document, so freeing that node will free the entire document.
All this works well for immutable objects and RTFs, but does not allow my mutable variables to work cleanly. This is quite annoying.
I need to allow a variable to hold a nodeset, a document, or a scalar value, without caring about the previous value. But I need to hold on to the previous values to allow others to refer to them without dangling references. Dangling References
Consider the following input document:
<top>
<x1/>
<x2/>
<x3/>
</top>
The following code makes a nodeset (type XPATH_NODESET) whose nodeTab array points into the input document:
var $x = top/*[starts-with("x", name())];
The following code make an RTF/RVT (type XPATH_XSLT_TREE), whose "fake" document contains a root element (type XML_DOCUMENT_NODE) that contains the "top" element node.
var $y = <top> {
<x1>;
<x2>;
<x3>;
}
The following code makes a nodeset (type XPATH_NODESET) that refers to nodes in the "fake" document under $y:
var $z = $y/*[starts-with("x", name())];
Now consider the following code:
mvar $z = $y/*[starts-with("x", name())];
var $a = $z[1];
if ($a) {
set $z = <rvt> "a"; /* RVT */
var $b = $z[1]; /* refers to nodes in "fake" $y doc */
set $z = <next> "b"; /* RVT */
var $c = $z[1]; /* refers to node in <next> RVT */
<a> $a;

---
*Synthesized by AutonomousLearner*
