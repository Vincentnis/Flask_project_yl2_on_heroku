from flask_restful import abort, Resource
from data import db_session
from flask import jsonify, request
from models.jobs import *
from models.categories import *
from rest_api.parsers import *
import datetime
from tests import abort_if_job_not_found


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'id': job_id,
                        'header': job.header,
                        'author': job.author,
                        'requirements': job.requirements,
                        'description': job.description,
                        'creation_date': job.creation_date,
                        'categories': [category.id - 1 for category in job.categories]
                        })

    def delete(self, job_id):
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, job_id):
        args = job_parser.parse_args()
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        job.header = args['header']
        job.requirements = args['requirements']
        job.description = args['description']
        job.creation_date = datetime.datetime.now()
        form = request.json['form']
        new_categories = set([session.query(Category).get(id + 1) for id in form['select_data']])
        old_categories = set(job.categories)
        for old_category in old_categories - new_categories:
            job.categories.remove(old_category)
        for new_category in new_categories - old_categories:
            job.categories.append(new_category)
        if form['add_category_data']:
            category = Category()
            category.name = form['name_of_category']
            job.categories.append(category)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs)
        return jsonify(
            {
                'jobs':
                    [{'id': job.id,
                      'header': job.header,
                      'author': job.author,
                      'requirements': job.requirements,
                      'description': job.description,
                      'creation_date': job.creation_date,
                      'categories': [category.id - 1 for category in job.categories]
                      } for job in jobs]
            }
        )

    def post(self):
        args = job_parser.parse_args()
        session = db_session.create_session()
        job = Jobs(header=args['header'],
                   requirements=args['requirements'],
                   description=args['description'],
                   author=args['author'])
        form = request.json['form']
        for category_name in [form['choices'][val][1] for val in form['select_data']]:
            category = session.query(Category).filter(Category.name == category_name).first()
            job.categories.append(category)
        if form['add_category_data']:
            category = Category()
            category.name = form['name_of_category']
            job.categories.append(category)
        session.add(job)
        session.commit()
        return jsonify({'success': "OK"})
