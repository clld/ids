<%inherit file="app.mako"/>
<%block name="title">${_('Home')}</%block>
##
## define app-level blocks:
##
<%block name="brand">
    <a href="${request.resource_url(request.dataset)}" class="brand">IDS</a>
</%block>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/charissil.css')}" rel="stylesheet">
</%block>

${next.body()}
