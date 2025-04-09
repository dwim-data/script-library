import requests
from graphql import build_client_schema, print_schema

# Step 1: Define the Introspection Query
INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args {
        ...InputValue
      }
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
        }
      }
    }
  }
}
"""


# Step 2: Send the Introspection Query
def fetch_introspection_schema(endpoint_url):
    response = requests.post(url=endpoint_url, json={"query": INTROSPECTION_QUERY})
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(
            f"Query failed with status code {response.status_code}: {response.text}"
        )


# Step 3: Convert Introspection Data to SDL
def generate_sdl_from_introspection(endpoint_url):
    introspection_data = fetch_introspection_schema(endpoint_url)
    schema = build_client_schema(introspection_data)
    sdl = print_schema(schema)
    return sdl
