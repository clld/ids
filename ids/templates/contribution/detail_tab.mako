chapter_id	entry_id	meaning	${ctx.name|n}_${ctx.valuesets[0].values[0].description}
% for vs in ctx.valuesets:
${vs.parameter.chapter.id}	${vs.parameter.id.split('-')[1]}	${vs.parameter.name|n}	${'; '.join(v.name for v in vs.values)|n}
% endfor