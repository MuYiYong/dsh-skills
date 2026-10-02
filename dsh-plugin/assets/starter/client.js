window.__ModuleLoader__.load({
  id: '__PACKAGE__',
  factory(require) {
    const React = require('react');
    const h = React.createElement;
    const namespace = '__ID__';
    const copy = {
      zh: {
        title: '本体应用接入示例',
        description: '此面板验证插件接入，尚未连接业务数据。',
        details: '开发下一步',
        next: '接入实体与关系数据，添加证据查看，并将完整工作台放入合适的页面 slot。',
      },
      en: {
        title: 'Ontology integration starter',
        description: 'This panel checks plugin integration. No business data is connected.',
        details: 'Development next steps',
        next: 'Connect entities and relations, add evidence inspection, and use a page slot for the full workbench.',
      },
    };
    const css = `
      [data-__ID__] { box-sizing: border-box; min-width: 0; width: 100%;
        padding: 12px 16px; color: var(--dsw-alias-label-primary);
        background: var(--dsw-alias-bg-base); border: 1px solid var(--dsw-alias-border-l1);
        border-radius: 12px; font: inherit; line-height: 1.5; overflow-wrap: anywhere; }
      [data-__ID__] p { margin: 4px 0 0; color: var(--dsw-alias-label-secondary); }
      [data-__ID__] summary { cursor: pointer; margin-top: 8px;
        color: var(--dsw-alias-state-business-primary); }
      [data-__ID__] summary:focus-visible { outline: 2px solid var(--dsw-alias-state-business-primary); outline-offset: 3px; }
    `;
    function Panel({ t, subject }) {
      if (subject.kind !== 'bundle' || subject.pkg.name !== '__PACKAGE__') return null;
      return h('section', { 'data-__ID__': '', 'aria-label': t('title') },
        h('style', null, css),
        h('strong', null, t('title')),
        h('p', null, t('description')),
        h('details', null, h('summary', null, t('details')), h('p', null, t('next'))));
    }
    return {
      inject: ['slots', 'locale'],
      apply(ctx) {
        ctx.effect(() => ctx.locale.register(namespace, copy));
        ctx.slots.inject('plugins.detail.section', () => ctx.slots.register({
          name: 'plugins.detail.section', id: '__ID__', locale: namespace, order: 5,
        }, Panel));
      },
    };
  },
});
