# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import datetime
from dateutil.relativedelta import relativedelta
from trytond.wizard import Wizard, StateAction
from trytond.pyson import PYSONEncoder
from trytond.transaction import Transaction
from trytond.pool import Pool


__all__ = ['ProductMoves']


class ProductMoves(Wizard):
    'Moves by product'
    __name__ = 'product.moves'
    start = StateAction('stock.act_move_form')

    def search_value_moves(self):
        now = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)-relativedelta(years=1)
        return [('create_date', '>=', now)]

    def do_start(self, action):
        pool = Pool()
        Product = pool.get('product.product')
        Template = pool.get('product.template')

        context = Transaction().context
        prod_ids = context['active_ids']

        codes = set()
        if context['active_model'] == 'product.template':
            for template in Template.search([('id', 'in', prod_ids)]):
                for product in template.products:
                    codes.add(product.code or product.name)
        else:
            for product in Product.search([('id', 'in', prod_ids)]):
                codes.add(product.code or product.name)

        search_value = self.search_value_moves()

        domain = [('product', '=', code) for code in codes]
        if len(codes) > 1:
            domain.insert(0, 'OR')
            search_value += [domain]
        else:
            search_value += domain

        action['pyson_search_value'] = PYSONEncoder().encode(search_value)

        # rename title tab
        action['name'] += ' - %s' % (', '.join(codes))
        return action, {}
