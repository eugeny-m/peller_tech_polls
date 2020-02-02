import aiohttp_jinja2
from aiohttp import web

from . import db


@aiohttp_jinja2.template('admin/admin_base.html')
async def admin_index(request):
    return {'title': 'Admin'}


class BaseListCreateView(web.View):
    list_template_name = 'admin/admin_model_list.html'
    detail_template_name = 'admin/admin_model_detail.html'
    model = None
    title = 'Enter title'  # Model name for template title

    def get_column_names(self):
        columns = []

        for column in self.model.columns:
            if column.name == 'id':
                continue
            columns.append(column.name)

        columns = sorted(columns)
        columns = ['id'] + columns
        return columns

    # list view
    async def get(self):

        columns = self.get_column_names()

        async with self.request.app['db'].acquire() as conn:
            records = await db.get_list(conn, self.model)

            # get list of records values tuples
            # with ordering as columns
            formatted_records = []
            for record in records:
                formatted_records.append([
                    getattr(record, c) for c in columns
                ])

            context = {
                'records': formatted_records,
                'title': self.title,
                'columns': columns,
            }
            return aiohttp_jinja2.render_template(
                request=self.request,
                context=context,
                template_name=self.list_template_name,
            )

    # create view
    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            context = await db.get_list(conn, self.model)
            return aiohttp_jinja2.render_template(
                request=self.request,
                context=context,
                template_name=self.detail_template_name
            )


class PollListCreateView(BaseListCreateView):
    model = db.poll
    title = 'Poll'


class QuestionListCreateView(BaseListCreateView):
    model = db.question
    title = 'Question'


class ChoiceListCreateView(BaseListCreateView):
    model = db.choice
    title = 'Choice'
