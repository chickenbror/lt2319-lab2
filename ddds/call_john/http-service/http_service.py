# -*- coding: utf-8 -*-

import json

from flask import Flask, request
from jinja2 import Environment

app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter

with open('contacts.json', "r") as json_file:
    CONTACT = json.load(json_file)
    # CONTACT['contact_Name']['mobile/work/home'] = 'number_str'


def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/get_number", methods=['POST'])
def get_number():

  # Reads payload for (selected_contact, phone_type) => returns number
  payload = request.get_json()
  contact_name = payload["context"]["facts"]["selected_contact"]["value"]
  phone_type = payload["context"]["facts"]["phone_type"]["value"]

  # Name not in contact
  if contact_name not in CONTACT:
      response_value = 'Contact does not exist'
      return query_response(value=response_value, grammar_entry=None)
  # Name is in contact, but data is None or data contains no phone_type
  phone_types = CONTACT[contact_name] if CONTACT[contact_name] else [None]
  if phone_type not in phone_types:
      response_value = f'The contact has no {phone_type} number'
      return query_response(value=response_value, grammar_entry=None)
  # Name and phone_type both exists
  response_value = CONTACT[contact_name][phone_type]
  return query_response(value=response_value, grammar_entry=None)

