chapter_id	entry_id	meaning	${ctx.name|n}_${ctx.default_representation} ${'_'.join([ctx.name, ctx.alt_representation]) + '\t' if ctx.alt_representation else ''|}comment
% for vs in sorted(ctx.valuesets, key=lambda vs: tuple(int(c) for c in vs.parameter.id.split('-'))):
${vs.parameter.chapter.id}	${vs.parameter.id.split('-')[1]}	${vs.parameter.name|n}	${'; '.join(v.name for v in vs.values)|n}   ${vs.alt_representation + '\t' if ctx.alt_representation else ''|n}${vs.comment|n}
% endfor