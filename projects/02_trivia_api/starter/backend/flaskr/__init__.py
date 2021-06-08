import os
from flask import (
  Flask,
  request,
  abort,
  jsonify)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql import func


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


# gets the category records, ordered by id in a dictionary
# where the key is the category id and the value is the category name
def get_categories():
    selection = Category.query.order_by(Category.id).all()

    categories = {}
    for category in selection:
        # converts category id from int to string with str
        categories[str(category.id)] = category.type

    return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # add CORS
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
          'Access-Control-Allow-Headers',
          'Content-Type,Authorization,true')
        response.headers.add(
          'Access-Control-Allow-Methods',
          'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Handle GET requests for all available categories.
    @app.route('/categories')
    def retrieve_categories():
        categories = get_categories()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'categories': categories
        })

    # Handle GET requests for questions,
    # including pagination (every 10 questions).
    # This endpoint return a list of questions,
    # number of total questions, current category, categories.
    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': get_categories(),
            'current_category': ''
        })

    # This endpoint DELETE question using a question ID.
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
            })

        except():
            abort(422)

    # This endpoint handle POST a new question and
    # to get questions based on a search term.
    # For a new question require the question and answer text,
    # category, and difficulty score.
    # When get question based on a search term return any questions
    # for whom the search term is a substring of the question.
    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()

            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')
            search = body.get('searchTerm')

            try:
                if search:
                    selection = Question.query.order_by(Question.id)\
                      .filter(Question.question.ilike('%{}%'.format(search)))
                    current_questions = paginate_questions(request, selection)

                    if len(current_questions) == 0:
                        return jsonify({
                            'success': False,
                            'questions': current_questions,
                            'total_questions': 0,
                            'current_category': ''
                        })
                        abort(404)

                    return jsonify({
                        'success': True,
                        'questions': current_questions,
                        'total_questions': len(selection.all()),
                        'current_category': ''
                    })

                else:
                    if not search and search is not None:
                        return jsonify({
                            'success': False,
                            'questions': [],
                            'total_questions': 0,
                            'current_category': ''
                        })

                    elif new_question and new_answer and new_difficulty and \
                            new_category:

                        question = Question(
                          question=new_question,
                          answer=new_answer,
                          difficulty=new_difficulty,
                          category=new_category)

                        question.insert()

                        selection = Question.query.order_by(Question.id).all()
                        current_questions = paginate_questions(
                          request,
                          selection)

                        return jsonify({
                            'success': True
                        })
                    else:
                        return jsonify({
                            'success': False
                        })

            except():
                abort(422)

        except():
            abort(405)

    # This endpoint get questions based on category.
    @app.route('/categories/<int:id>/questions')
    def retrieve_questions_by_category(id):

        selection = Question.query.order_by(Question.id)\
          .filter(Question.category == id)
        current_questions = paginate_questions(request, selection)
        category = Category.query.get(id)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection.all()),
          'current_category': category.type
        })

    # This endpoint get questions to play the quiz.
    # Take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.
    @app.route('/quizzes', methods=['POST'])
    def get_question_play_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        id_category = int(quiz_category['id'])

        # get a random question regardless of the category
        if id_category == 0:
            question = Question.query\
              .filter(Question.id.notin_(previous_questions))\
              .order_by(func.random()).first()
        else:
            # get a random question within the given category.
            question = Question.query\
                .filter(Question.category == id_category)\
                .filter(Question.id.notin_(previous_questions))\
                .order_by(func.random()).first()

        if question is None:
            abort(404)

        question = question.format()

        return jsonify({
          'success': True,
          'question': question
        })

    # Error handlers.
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
