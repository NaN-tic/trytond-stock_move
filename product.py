# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import datetime
from trytond.wizard import Wizard, StateAction
from trytond.pyson import PYSONEncoder
from trytond.transaction import Transaction
from trytond.pool import Pool


__all__ = ['ProductMoves']


class ProductMoves(Wizard):
    'Moves by product'
    __name__ = 'product.moves'
    start = StateAction('stock.act_move_form')

    def do_start(self, action):
        pool = Pool()
        Product = pool.get('product.product')
        Template = pool.get('product.template')

        context = Transaction().context
        prod_ids = context['active_ids']

        product_ids = []
        codes = []
        if context['active_model'] == 'product.template':
            for template in Template.search([('id', 'in', prod_ids)]):
                for product in template.products:
                    product_ids.append(product.id)
                    codes.append(product.code or product.name)
        else:
            for product in Product.search([('id', 'in', prod_ids)]):
                product_ids.append(product.id)
                codes.append(product.code or product.name)

        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        search_value = [
            ('create_date', '>=', now),
            ]

        if len(product_ids) > 0:
            domain = ['OR']
            for prod_id in product_ids:
                domain.append(('product', '=', prod_id))
            search_value += [domain]
        else:
            search_value.append(('product', '=', product_ids[0]))

        action['pyson_search_value'] = PYSONEncoder().encode(search_value)

        # rename title tab
        action['name'] += ' - %s' % (', '.join(codes))
        return action, {}
