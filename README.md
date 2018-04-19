# itoptop package for python3

## Install
    pip install itoptop

## Usage
    from itoptop import Itop
    url = 'https://itop_servername/webservices/rest.php'
    ver = '1.3'
    usr = 'user'
    pwd = 'password'
    data_model = 'path/to/datamodel.xml' # default is itop_folder/data/datamodel-production.xml

### With Data Model
    itop = Itop(url, ver, usr, pwd, data_model)
Get id from Organization which code is SOMECODE

    query = {'code': 'SOMECODE'}
    projection = ['id']
    result = itop.Organization.find(query, projection)

Insert list of person

    object_list = [
      {'name': 'NAME', 'first_name': 'FIRST_NAME', 'org_name': 'My Company/Department'},
      {'name': 'NAME', 'first_name': 'OTHER_NAME', 'org_name': 'My Company/Department'}
    ]
    result = itop.Person.insert(object_list)

Update field first_name to FIRST_NAME and Organization relationship to My Company/Department in person where name is NAME

    query= {'name': 'NAME'}
    update = {'first_name': 'FIRST_NAME', 'org_name': 'My Company/Department'}
    result = itop.Person.update(query, update, multi=True, upsert=True)

Remove all persons which Name is NAME and First Name is FIRST_NAME

    result = itop.Person.remove({'name': 'NAME', 'first_name': 'FIRST_NAME'})

### Without Data Model
    itop = Itop(uri, ver, usr, pwd)
Get id from Organization which code is SOMECODE

    query = {'code': 'SOMECODE'}
    projection = ['id']
    result = itop.schema('Organization).find(query, projection)

Insert list of person

    object_list = [
      {'name': 'NAME', 'first_name': 'FIRST_NAME', 'org_id': 1},
      {'name': 'NAME', 'first_name': 'OTHER_NAME', 'org_id': 1}
    ]
    result = itop.schema('Person').insert(object_list)

Update field first_name to FIRST_NAME and org_id to 2 of objects in person where name is NAME

    query= {'name': 'NAME'}
    update = {'first_name': 'FIRST_NAME', 'org_id': 1}
    result = itop.schema('Person').update(query, update, multi=True, upsert=True)

Remove all persons which Name is NAME and First Name is FIRST_NAME

    result = itop.schema('Person').remove({'name': 'NAME', 'first_name': 'FIRST_NAME'})

## Contributing
Pull requests for new features, bug fixes, and suggestions are welcome!

## License
GNU General Public License v3 (GPLv3)
