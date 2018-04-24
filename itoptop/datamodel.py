class DataModel(object):
    def __init__(self, filename):
        """
        Create Data Model
        :param filename:
        """
        import re
        from lxml import etree
        xml = open(filename, encoding='utf-8', errors='replace').read()
        xml = re.sub('xmlns(:xsi|)="[^"]+"', '', xml, count=1)
        xml = re.sub('xsi:', '', xml, count=0)
        xml = bytes(bytearray(xml, encoding='utf-8'))
        self.root = etree.XML(xml)

        schemas = [node for node in self.root.xpath("//class") if 'id' in node.attrib]
        self.schemas = [schema.attrib['id'] for schema in schemas]  # TODO: get only user visible schemas  

        self.lookups = {}

    def lookup(self, schema):
        """
        Quando um campo externo é enviado para uma inclusão/inserção, o iTop retorna um erro e não faz a referência ao
        item relacionado automaticamente.

        Desta forma, é necessário buscar o id do item, incluí-lo no objeto a ser inserido/atualizado e remover o campo
        externo.

        Exemplo:
        Inclusão do objeto abaixo na Classe Organization ocorre erro.
            {'name': 'Name', 'parent_name': 'Parent Name'}
        Entretanto, objeto abaixo insere corretamente:
            {'name': 'Name', 'parent_id': <number>}

        Como é feito:


        :param schema:
        :return:
        """

        if schema in self.lookups:
            return self.lookups[schema]
        root = self.root

        schema_lookups = {}
        extfields = list(set(root.xpath("//class[@id='%s']//field[@type='AttributeExternalField']/@id" % schema)))
        for extfield in extfields:
            key = root.xpath("//class[@id='%s']//field[@id='%s']/extkey_attcode/text()" % (schema, extfield))[0]
            lookup_field = \
                root.xpath("//class[@id='%s']//field[@id='%s']/target_attcode/text()" % (schema, extfield))[0]
            if root.xpath("//class[@id='%s']//field[@id='%s']/@type" % (schema, key))[0] == 'AttributeHierarchicalKey':
                lookup_schema = schema
            else:
                target_class = root.xpath("//class[@id='%s']//field[@id='%s']/target_class/text()" % (schema, key))[0]
                lookup_schema = target_class
            schema_lookups[extfield] = (key, lookup_schema, lookup_field)

        parent = root.xpath("//class[@id='%s']/parent/text()" % schema)
        if len(parent) > 0:
            parent = parent[0]
            if parent != 'cmdbAbstractObject':  # TODO: improve this
                import copy
                lookups_inheritance = copy.deepcopy(self.lookup(parent))
                lookups_inheritance.update(schema_lookups)
                schema_lookups = lookups_inheritance

        self.lookups[schema] = schema_lookups
        return schema_lookups
