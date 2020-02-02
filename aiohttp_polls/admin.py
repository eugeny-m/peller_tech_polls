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
    list_view_name = None
    detail_view_name = None

    def get_column_names(self):
        columns = []

        for column in self.model.columns:
            if column.name == 'id':
                continue
            columns.append(column.name)

        columns = sorted(columns)
        return columns

    # list/detail view
    async def get(self):
        obj_id = self.request.match_info.get('id', None)
        if obj_id is not None:
            return await self.detail(int(obj_id))

        else:
            return await self.list()

    # create/edit view
    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            context = await db.get_list(conn, self.model)
            return aiohttp_jinja2.render_template(
                request=self.request,
                context=context,
                template_name=self.detail_template_name
            )

    # list view
    async def list(self):
        columns = self.get_column_names()
        async with self.request.app['db'].acquire() as conn:
            records = await db.get_list(conn, self.model)

            # get list of records values tuples
            # with ordering as columns
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'values': [getattr(record, c) for c in columns],
                    'id': getattr(record, 'id', None),
                })

            context = {
                'records': formatted_records,
                'title': self.title,
                'columns': columns,
                'detail_view_name': self.detail_view_name,
            }
            return aiohttp_jinja2.render_template(
                request=self.request,
                context=context,
                template_name=self.list_template_name,
            )

    # detail view
    async def detail(self, obj_id):
        """
        this method generate html form with all object fields except ID field
        :param obj_id:
        :return:
        """

        async with self.request.app['db'].acquire() as conn:
            obj = await db.get_object(conn, self.model, obj_id)
            fields = []
            foreign_keys = {f.parent.name: f for f in self.model.foreign_keys}
            print(foreign_keys)

            for column in self.model.columns:

                # could be VARCHAR(200), cutting part in the brackets
                field_type = str(column.type).split('(')[0]
                # foreign key parents
                parents = None

                if column.name == 'id':
                    continue

                # for foreignkey fields
                # we get parents to show in form select
                if column.name in foreign_keys:
                    field_type = 'SELECT'
                    parents = []

                    f_key = foreign_keys[column.name]
                    parent_records = await db.get_list(
                        conn,
                        f_key.column.table
                    )

                    # generate parents list for select options
                    for parent in parent_records:
                        # to chose selected foreign key value
                        selected = getattr(obj, column.name) == parent.id
                        parents.append({
                            'id': parent.id,
                            'value': repr(dict(parent)),
                            'selected': selected
                        })

                fields.append({
                    'name': column.name,
                    'value': getattr(obj, column.name),
                    'type': field_type,
                    'parents': parents,
                })

            context = {
                'title': self.title,
                'detail_view_name': self.detail_view_name,
                'object': obj,
                'fields': fields,

            }
            return aiohttp_jinja2.render_template(
                request=self.request,
                context=context,
                template_name=self.detail_template_name
            )


class PollListCreateView(BaseListCreateView):
    model = db.poll
    title = 'Poll'
    list_view_name = 'admin_poll_list'
    detail_view_name = 'admin_poll'


class QuestionListCreateView(BaseListCreateView):
    model = db.question
    title = 'Question'
    list_view_name = 'admin_question_list'
    detail_view_name = 'admin_question'


class ChoiceListCreateView(BaseListCreateView):
    model = db.choice
    title = 'Choice'
    list_view_name = 'admin_choice_list'
    detail_view_name = 'admin_choice'
