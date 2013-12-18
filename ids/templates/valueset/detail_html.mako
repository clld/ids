<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Counterparts in ${h.link(request, ctx.language)} for meaning "${h.link(request, ctx.parameter)}"</h2>

<ul class="unstyled">
% for i, value in enumerate(ctx.values):
    <li>${value.name} (${value.description})</li>
% endfor
</ul>
% if ctx.jsondatadict['comment']:
<p>${ctx.jsondatadict['comment']}</p>
% endif
<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">${_('Contribution')}:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.contribution)}
        by
        ${h.linked_contributors(request, ctx.contribution)}
        ${h.button('cite', onclick=h.JSModal.show(ctx.contribution.name, request.resource_url(ctx.contribution, ext='md.html')))}
    </dd>
    <dt class="parameter">${_('Parameter')}:</dt>
    <dd class="parameter">${h.link(request, ctx.parameter)}</dd>
</dl>
</div>
</%def>
