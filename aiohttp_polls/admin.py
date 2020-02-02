import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import authorized_userid

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

    # view control methods

    # list/detail view
    async def get(self):
        username = await authorized_userid(self.request)
        if not username:
            return web.HTTPFound('/login')

        if 'add' in self.request.query:
            return await self.detail(obj_id=None)

        obj_id = self.request.match_info.get('id', None)
        if obj_id is not None:
            return await self.detail(int(obj_id))

        else:
            return await self.list()

    # create/edit view
    async def post(self):
        username = await authorized_userid(self.request)
        if not username:
            return web.HTTPFound('/login')

        obj_id = self.request.match_info.get('id', None)
        if obj_id is not None:
            return await self.edit(int(obj_id))

        else:
            return await self.create()

    # help methods

    def get_column_names(self):
        columns = []

        for column in self.model.columns:
            if column.name == 'id':
                continue
            columns.append(column.name)

        columns = sorted(columns)
        return columns

    def get_context(self):
        return {
            'detail_template_name': self.detail_template_name,
            'list_template_name': self.list_view_name,
            'list_view_name': self.list_view_name,
            'detail_view_name': self.detail_view_name,
            'title': self.title,
        }

    # POST methods

    # create view
    async def create(self):
        data = await self.request.post()
        async with self.request.app['db'].acquire() as conn:
            await db.create_object(conn, self.model, data)
            return await self.list()

    # edit view
    async def edit(self, obj_id):
        data = await self.request.post()
        async with self.request.app['db'].acquire() as conn:
            await db.update_object(conn, self.model, obj_id, data)
            return await self.list()

    # GET methods

    # list view
    async def list(self):
        columns = self.get_column_names()
        async with self.request.app['db'].acquire() as conn:
            records = await db.get_list(conn, self.model)

            # get list of records {'values': [..], 'id': 1}
            # with values ordered as columns
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'values': [getattr(record, c) for c in columns],
                    'id': getattr(record, 'id', None),
                })
            context = self.get_context()
            context.update({
                'records': formatted_records,
                'columns': columns,
            })
            return aiohttp_jinja2.render_template(
                request=self.request,
                context=context,
                template_name=self.list_template_name,
            )

    # detail view
    async def detail(self, obj_id=None):
        """
        this method generate html form with all object
        fields except ID field.
        If obj_id is not None all inputs will be
        filled from object

        :param obj_id: int or None
        :return: List View
        """

        async with self.request.app['db'].acquire() as conn:
            if obj_id is None:
                obj = None
            else:
                obj = await db.get_object(conn, self.model, obj_id)

            fields = []
            foreign_keys = {f.parent.name: f for f in self.model.foreign_keys}

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
                        selected = False
                        if obj:
                            selected = getattr(obj, column.name) == parent.id
                        parents.append({
                            'id': parent.id,
                            'value': repr(dict(parent)),
                            'selected': selected
                        })

                field = {
                    'name': column.name,
                    'type': field_type,
                    'parents': parents,
                }
                if obj:
                    field['value'] = getattr(obj, column.name)
                fields.append(field)

            context = self.get_context()
            context['object'] = obj
            context['fields'] = fields

            return aiohttp_jinja2.render_template(
                request=self.request,
                context=context,
                template_name=self.detail_template_name
            )


class PollAdmin(BaseListCreateView):
    model = db.poll
    title = 'Poll'
    list_view_name = 'admin_poll_list'
    detail_view_name = 'admin_poll'


class QuestionAdmin(BaseListCreateView):
    model = db.question
    title = 'Question'
    list_view_name = 'admin_question_list'
    detail_view_name = 'admin_question'


class ChoiceAdmin(BaseListCreateView):
    model = db.choice
    title = 'Choice'
    list_view_name = 'admin_choice_list'
    detail_view_name = 'admin_choice'
