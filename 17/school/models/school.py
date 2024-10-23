from odoo import models, fields, api



"""#################  PROTOTYPE // SAME MODEL //  EXTENDED INHERITANCE  : ################"""

# used to Inherit for current model (School Model/ Folder)
# its required to give access rights for this class.
# no need to add the inherited module in 'depends' of __manifest__.py.
# no need to Create proper views for this inherited model in views of this module
# just add fields in xml view of inherited model as normally added.
# Update your module to apply the changes.
class Address(models.Model):
    _name = 'address'
    city = fields.Text(string="Address")

class SchoolProfile(models.Model): #SchoolProfile is a class name of python
    _name = 'school.profile' #school.profile is a table name in database
    _inherit = 'address'
    _rec_name = 'name'
    # The _rec_name attribute defines which field to use as the display name for records, especially in Many2one relationships,
    # when the name field is absent or unsuitable. It's crucial for models without a name field, enabling a custom pattern (e.g., product code) to represent records.

    _description = 'School Profile Page' #School Profile page is a description

    name = fields.Char(string="School Name", copy=False) #primary key   # use it as Many2one field in studunt model

    email = fields.Char(string="Email" , copy=False) #primary key
    phone = fields.Char(string="Phone", copy=False) #primary key and COPY = FALSE means it is not show when creating / coping new duplicate record
    rank = fields.Integer(string="Rank",copy=False) #primary key
    virtual_class = fields.Boolean(string="Virtual Class",default=1) #Boolean field is used for tick and untick / 1 and 0 /  true and false
    result = fields.Float(string="Result")
    address = fields.Text(string="Address")
    establish_date = fields.Date(string="Establishment Date")
    open_date = fields.Datetime(string="Opening Date")
    school_number = fields.Char(string="School Number")


    school_type = fields.Selection([('public',"Public School"),('private',"Private School")]
                                   ,help = "Select type of School") #Selection have field type which contains list of tuple

    document = fields.Binary(string="Document")  #binary field used for uploading file
    document_name = fields.Char(string="Document Name")
    image = fields.Image("Image", max_width=80, max_height=80 ) #image field used for uploading image
    description = fields.Html(string="Description") #Html field used for text editor and text area , it also used in field of form view ex: widget="html"

    """################  SQL Constraint : ################"""
    _sql_constraints = [ ('unique_name', 'UNIQUE(name)', 'School names must be unique!') ] # tuple in a list
            # these are rules applied to database tables to ensure data integrity.
            # 'unique_field' : A constraint that ensures that the Field is unique. // these are rules applied to database tables to ensure data integrity.
            # 'UNIQUE(field)' :  field must have unique values across all records in the table. // condition for unique field
            # Error Message : An error message that will be displayed if the constraint is violated.



    """################    Reference field : ################"""
    # Reference field  provides a dynamic way to establish relationships between models.
    # Unlike traditional Many2One fields that link to predefined models, REFERENCE fields allow users to select from both the related model and a specific record from a selection list.
    ref_id = fields.Reference(selection=[("school.profile","School"),("account.move","Invoice"),("hobby","Hobby")], string="Reference") # Return a list of tuples, where each tuple contains the model name and its human-readable label.


    """################  Computed Field , Dependencies and @api.depends : ################"""
    ## used to automate calculations and derive values based on predefined functions , ensuring data accuracy and reducing manual effort.
    # auto_rank = fields.Integer( string="Auto Rank" ,store = True ) #  store = True attributes is used to STORE the field record in the DATABASE
    auto_rank = fields.Integer(compute="_auto_rank_populate" , string="Auto Rank",store = True ) #  store = True attributes is used to STORE the field record in the DATABASE
    #

    @api.depends('school_type')                # compute attribute that specifies the function responsible for calculation.
    def _auto_rank_populate(self): # When any of those dependencies change, this method will be triggered to update the computed value.
        for rec in self:         # It's commonly used for dynamically computed fields or methods that rely on other field values or context information.
            if rec.school_type == 'public':
                rec.auto_rank = 50
                rec.virtual_class = False
                print("rec.virtual_class : ",rec.virtual_class)
            elif rec.school_type == 'private':
                rec.auto_rank = 100
                rec.virtual_class = True
                print("rec.virtual_class : ",rec.virtual_class)
            else:
                rec.auto_rank = 0
                rec.virtual_class = False

    """#################  WRITE METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method
    # def write_orm(self):
    #     print(self.school_type)
    #     if self.school_type == 'public':
    #         val = {'virtual_class': False}
    #     elif self.school_type == 'private':
    #         val = {'virtual_class': True}
    #     else:
    #         val = {'virtual_class': False}
    #     record = self.env['school.profile'].browse([7,12,13]).write(val)  # return true or false
    #                                         # browse method return id of recordset
    #     print("record..............", record) # print true or false

        # if val.get('school_type') == 'public':
        #     val['virtual_class'] = False
        # elif val.get('school_type') == 'private':
        #     val['virtual_class'] = True
        # record = super(SchoolProfile, self).write(val)
        # print("record..............", record) # print true or false

    """#################  NAME_CREATE METHOD : ################"""
    # # # Create a new record by calling :meth:`create()` with only one value provided: the display name of the new record.
    # @api.model
    # def name_create(self, name):
    #     # print("name_create",name)
    #     # print("self : : : ",self)
    #     # rtn = super(SchoolProfile,self).name_create(name) # create a new school record in student page
    #     # print("rtn : : : ",rtn)
    #     # return rtn
    #     # Return a "Tuple" which contain (id, display_name) pair value of the created record
    #
    #     rtn = self.create({'name': name}) # create a new school record in student page
    #     print("rtn : ", rtn.id, rtn.display_name)
    #     return rtn.id, rtn.display_name # Return type : tuple
    #     # Returns (id, display_name) pair value of the created record in tuple


    """#################  NAME_GET METHOD : ################"""
    """The `name_get` method has been deprecated in Odoo 16.4 and is now based on `display_name`, reversing the previous approach."""
    # Return a list of tuples, where each tuple contains the model name and its human-readable label.

    # def name_get(self):
    #     student_list = []
    #     for school in self:
    #         name = school.name
    #         if school.school_type :
    #             name += " ({})".format(name.school_type)
    #         student_list.append((school.id, name))
    #     return student_list

    """#################  SEARCH METHOD : ################"""
    # # # # there is no need of decorator @api.model or @api.multi in write method
    # # """self.env['model.name'].search( [ ('field','operator(=,>,<)','value') ] , limit = None, offset = 0, order ='id'//None))"""
    # # #     - **domain** – Use an empty list to match all records.**`[('field','operator(=,>,<)','value')]`**
    # # #     - **limit** – maximum number of records to return **(default: all) `limit = None`**
    # # #     - **offset** – number of results to ignore//skip **(default: None) `offset = 0`**
    # # #     - **order** – sort by given field string **(default = 'id') `order = 'id'//None`**
    #

    # def search_orm(self):
    #     record = self.env['school.profile'].search([])  # return recordset
    #     print("record..............", record)  # print recordset
    #     for r in record:
    #         print("r",r, r.name)  # print recordset with name



    """#################  UNLINK METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method
    #
    # def unlink_orm(self):
    #     record = self.env['school.profile'].browse([37,38]).unlink()  # return true or false
    #     # browse method return id of recordset
    #     print("record..............", record)  # print true or false










# questions :

# Update DB Query
# Constructor in class (oops)
# Type of Inheritance (oops)
# static method (opps)
# type of datatypes
# Meaning of override and overloading
# super method use case
# Add / Update an element in Dictionary of list
# remove an element in List from last
# use order parameter in search
# default method works
# Type of Action in Odoo
# @api.model and @api.multi use case
# Differentiate 3 model and explain all