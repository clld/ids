<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Words in ${h.link(request, ctx.language)} for meaning ${ctx.parameter.id} "${h.link(request, ctx.parameter)}"</h2>

<table class="table table-nonfluid">
% if ctx.language.dictionary.default_representation:
    <thead>
        <tr>
            <td>${ctx.language.dictionary.default_representation}</td>
            % if ctx.language.dictionary.alt_representation:
           <td>${ctx.language.dictionary.alt_representation}</td>
            % endif
        </tr>
    </thead>
% endif
    <tbody>
% for i, value in enumerate(ctx.values):
    <tr>
        <td>${h.link(request, value.word, class_='charissil')}</td>
        % if ctx.language.dictionary.alt_representation:
        <td class="charissil">${value.word.alt_name or ''}</td>
        % endif
    </tr>
% endfor
    </tbody>
</table>
% if ctx.jsondatadict.get('alt_representation'):
<h3>${ctx.jsondatadict['alt_representation'][0]} representation</h3>
<p>${ctx.jsondatadict['alt_representation'][1]}</p>
% endif
% if ctx.jsondatadict.get('comment'):
<h3>Comment</h3>
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
