import self

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import datetime


class school_student(models.Model):
    _name = 'school.student'
    _description = 'Student Profile Page' #School Profile page is a description

    roll_no = fields.Char("Roll No",readonly=False)
    name = fields.Char() # primary key
    gender = fields.Selection([('male','Male'),('female','Female')])
    active = fields.Boolean(string="Active",default=1)
    bdate = fields.Date(string="Birth Date",)
    age = fields.Integer(compute='_compute_age',string="Age",store=True)
    image = fields.Image(string="Image" )

    """################  Print pdf report using button click event : ################"""

    def print_custom_report(self):
        return self.env.ref('school_student.student_card_pdf_report').report_action(self)

    def _get_report_base_filename(self):
        return "Student Report"

    """################  Function call from XML WITHOUT parameters : ################"""
    # # We can use this method to call a function defined within any model without passing any parameters.
    # # this method is used to add roll number to the student profile
    # @api.model
    # def _change_roll_no(self):
    #     for stno in self.search([('roll_no','!=',False)]):
    #         stno.roll_no =  "STD"+str(stno.id)

    """################  Function call from XML WITH parameters : ################"""
    # We can use this method to call a function defined within any model WITH passing any parameters.
    # this method is used to add roll number to the student profile
    @api.model
    def _change_roll_no_with_para(self,add_string):
        for stno in self.search([('roll_no','=',False)]):
            stno.roll_no = add_string + "STD"+str(stno.id)

    """################  WIZARD ACTION : ################"""

    # Define a method to trigger the OBJECT BUTTON that opens the wizard in `models.py`.
    def wiz_open(self):
        # return self.env['ir.actions.act_window'].for_xml_id('school_student.student_fees_update_wizard')
        return {
            'name': 'Fees Update',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'student.fees.update.wizard',
            'target': 'new',
        }

    @api.depends('bdate')
    def _compute_age(self):
        for rec in self:
            if rec.bdate:
                # rec.age = fields.Date.today() - rec.bdate()
                rec.age = (fields.Date.today() - rec.bdate).days // 365
            else:
                rec.age = 0


    """################  PYTHON Constraint : ################"""
    # # @api.constrains('Field_name') - The decorator takes field names as arguments. These are the fields involved in the constraint.
    # # - Ensure certain conditions are met before saving a record.
    # # - automatically trigger validation checks when specified fields are modified
    # # - Used to enforce business rules by validating conditions before saving the record.
    @api.constrains('bdate')
    def _check_bdate(self):
        if self.bdate and self.bdate >= fields.Date.today():
            raise ValidationError('Birth date must be in the past')

    """################  SQL Constraint : ################"""

    """_sql_constraints = [ ('unique_name', 'UNIQUE(name)', 'Hobby names must be unique!') ]"""  # tuple in list
    # these are rules applied to database tables to ensure data integrity.
    # 'unique_field' : A constraint that ensures that the Field is unique. // these are rules applied to database tables to ensure data integrity.
    # 'UNIQUE(field)' :  field must have unique values across all records in the table. // condition for unique field
    # Error Message : An error message that will be displayed if the constraint is violated.

    # _sql_constraints = [ ('unique_name', 'UNIQUE(name)', 'Student names must be unique!') ]  # tuple in list

    """################    MONETARY field for CURRENCY  : ################"""
    currency_id = fields.Many2one('res.currency', string="Currency", default=20)  # This field represents a foreign key relationship (Many2One) to the 'res.currency' model.
    # Encapsulates a float expressed in a given res_currency.
    # 'res.currency' :  The name of the currency model (e.g., 'res.currency').
    # It allows you to link records in the current model to currency records.
    # - The 'res.currency' model represents different currencies (e.g., USD, EUR, GBP) used in the system.
    # - It provides information about currency symbols, decimal precision, and exchange rates.
    # - By default, the field name holding the related currency record is 'currency_id'.
    # - The decimal precision and currency symbol are automatically determined based on the related currency.
    student_fees = fields.Monetary(string="Student Fees" , index=True ,  ) # ,default=5000

    #### or (Another way to use MONETARY function as widget ) ####

    total_fees = fields.Float(string="Total Fees")  # set the fee field as a float field and in the XML file for fee field give a widget = monetary.



    """#################   Many2one field : ################"""
    # Connects multiple records from the current model to a single record in another model. Useful for hierarchical or parent-child relationships.
    """ field_id = fields.Many2one(comodel_name='model.model' (parent model) , string = 'Field Name' ) """
    # Multiple records from one / parent model relate to a single record in another child model.
    # In field_id , _id is mandatory for using Many2One.

    school_id = fields.Many2one('school.profile' , string="School Name" , required=True ) # it is Foreign Key in database
    # parent model = school.profile
    # child model = school.student
    # string  =  "Field Label": An optional label for the field (used in forms and   views).

    """#################   Many2many field :  ################"""
    #Connects multiple records in the current model to multiple records in another model. Useful for complex associations where records are linked in a bidirectional manner.
    """field_name = fields.Many2many('related.model', 'relation_table', 'current_model_field', 'related_model_field',string="Field Label")"""
    # 'related.model' / comoodel_name :  The name of the related model (e.g., 'hobby').
    # 'relation_DB_table_name': The name of the database table that stores the relationship (e.g., 'studunt_hobby_rel').
    # 'current_model_field' / column_1_name : The field in the current model that establishes the relationship (e.g., 'studunt_id').
    # 'related_model_field' / column_2_name : The field in the related model that establishes the relationship (e.g., 'hobby_id').
    # string  =  "Field Label": An optional label for the field (used in forms and views).

    hobby_list = fields.Many2many('hobby',"studunt_hobby_rel","studunt_id","hobby_id", string="Hobby List" , required=True )

    """################   Related field :  ################"""
    # You MUST have a Many2One field school_id linking to school.profile model.
    # Related fields in Odoo allow you to display the value of a field from a related model in the current model.
    # They are defined using the related attribute, specifying which field from the related model should be displayed.
    virtual_class = fields.Boolean(related="school_id.virtual_class" ,string="Virtual Class" ) # By default, related fields are read-only and not stored in the database.
    school_address = fields.Text(related="school_id.address" ,string="School Address" ,store=True  ) # If we want to store the field record in the database, Use store = True attributes.
    # related attribute, specifying which field from the related model should be displayed.




    #####################################################################################
    """################################ COMMON ORM METHODS #################################"""
    #####################################################################################

    # You should create a button in header of form in .xml file to call these methods.
    #################  CREATE METHOD : ################
    # there is no need of decorator @api.model or @api.multi in write method

    # def create_orm(self):
    #     # Assuming 'self' refers to an instance of the model
    #     val = {
    #         'name': 'Vivek',
    #         "gender" : 'male',
    #         "hobby_list" : [(6, 0, [1, 2, 3])],
    #     }
    #     record = self.env['school.student'].create(val) # return New Created recordset
    # given values of newly created record is in the dictionary
    #     print("record..............",record) # print id of New Created recordset

    """#################  COPY METHOD : ################"""
    # there is no need of decorator @api.model or @api.multi in write method

    # def copy_orm(self):
    #     val = {'name': 'Vivek',}
    #     record = self.env['school.student'].browse(11).copy(val)  # return New COPIED recordset
    #                                         # browse method return id of recordset
    #     print("record..............", record) # print id of New COPIED recordset

    """#################  WRITE METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method
    #
    # def write_orm(self):
    #     val = {
    #         'name': 'Vivek',
    #         "gender": 'female',
    #         "hobby_list": [(6, 0, [1, 2, 3])],
    #     }
    #     record = self.env['school.student'].browse(154).write(val)  # return true or false
    #                                         # browse method return id of recordset
    #     print("record..............", record) # print true or false

    """#################  IDs METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method
    # def ids_orm(self):
    #     record = self.env['school.student'].search([]).ids  # return List of ids
    #                                         # search method get recordset
    #     print("record..............", record)  # print List of ids

    """#################  ENV METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method
    # def env_orm(self):
    #     record = self.env['school.student']  # return List of ids
    #                                         # search method get recordset
    #     print("record..............", record)  # print List of ids

    """#################  UNLINK METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method
    #
    # def unlink_orm(self):
    #     record = self.env['school.student'].browse(153).unlink()  # return true or false
    #     # browse method return id of recordset
    #     print("record..............", record)  # print true or false

    """#################  BROWSE METHOD : ################"""
    # # # there is no need of decorator @api.model or @api.multi in write method
    # def browse_orm(self):
    #     record = self.env['school.student'].browse([8, 9])  # browse method return id of recordset
    #     for rec in record:
    #         print("record..............", rec.name)  # print name of recordset
    #

    """#################  SEARCH METHOD : ################"""
    # # # # there is no need of decorator @api.model or @api.multi in write method
    # # """self.env['model.name'].search( [ ('field','operator(=,>,<)','value') ] , limit = None, offset = 0, order ='id'//None))"""
    # # #     - **domain** – Use an empty list to match all records.**`[('field','operator(=,>,<)','value')]`**
    # # #     - **limit** – maximum number of records to return **(default: all) `limit = None`**
    # # #     - **offset** – number of results to ignore//skip **(default: None) `offset = 0`**
    # # #     - **order** – sort by given field string **(default = 'id') `order = 'id'//None`**
    #
    # def search_orm(self):
    #     record = self.env['school.student'].search([('active','=','True')],limit=None,offset=0,order='id')  # return recordset
    #     # browse method return id of recordset
    #     print("record..............", record)  # print all recordset
    #     for rec in record:
    #         print(rec) # print name of all recordset

    """#################  _SEARCH METHOD : ################"""

    # # # there is no need of decorator @api.model or @api.multi in write method
    # """self.env['model.name']._search( [ ('field','operator(=,>,<)','value') ] , limit = None, offset = 0, order ='id'//None))"""
    # #     - **domain** – Use an empty list to match all records.**`[('field','operator(=,>,<)','value')]`**
    # #     - **limit** – maximum number of records to return **(default: all) `limit = None`**
    # #     - **offset** – number of results to ignore//skip **(default: None) `offset = 0`**
    # #     - **order** – sort by given field string **(default = 'id') `order = 'id'//None`**
    # #     - **access_rights_uid** – to bypass access rights check, but not ir.rules!  **(default = 'id') `access_rights_uid = None**

    #  Private implementation of search() method, allowing specifying the uid to use for the access right check.


    # def search_orm(self):
    #     record = self._search(domain=[('gender', '=', 'male')], offset=0, limit=None, order=None,access_rights_uid=None)
    #     for ids in record:
    #         print("ids..............",ids) # print id of all recordset
    # # Returns : (in odoo17) SQL Query// (old odoo) list of ids  of the records that match the search criteria, not a recordset.

    """#################  SEARCH_COUNT METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method
    # def search_count_orm(self):
    #     record = self.env['school.student'].search_count([('active','=','True')])  # return count of all recordset
    #     # browse method return id of recordset
    #     print("record..............", record)  # print count of all recordset


    """#################  SEARCH_FETCH METHOD : ################"""
    # # there is no need of decorator @api.model or @api.multi in write method.
    # # Search for the records that satisfy the given domain search domain, and fetch the given fields to the cache.
    # # This method is like a combination of methods search() and fetch(), but it performs both tasks with a minimal number of SQL queries.

    # # **Syntax:** `self.env['model.name'].search([('field','operator(=,>,<)','value')], ['field_name'] , limit = None, offset = 0, order = 'id'//None))`
    # #
    # #     - **domain** – Use an empty list to match all records.**`[('field','operator(=,>,<)','value')]`**
    # #     - **limit** – maximum number of records to return **(default: all) `limit = None`**
    # #     - **`field_names`** - A collection of field names in a List that you want to retrieve for the matching records.
    # #     - **offset** – number of results to ignore//skip **(default: None) `offset = 0`**
    # #     - **order** – sort by given field string **(default = 'id') `order = 'id'//None`**
    # #
    # # - **`Returns : id`** : at most **limit** records matching the search criteria

    # def search_fetch_orm(self):
    #     record = self.env['school.student'].search_fetch([('gender','=','male')],['age'])  # return recordset ids
    #     print("record..............", record)  # print ids of all recordset
    #     for rec in record:
    #         print(rec.name,rec.gender)

    """#################  READ METHOD : ################"""
    # # # there is no need of decorator @api.model or @api.multi in write method
    # # Read the requested fields for the records in self, and return their values as a list of dictionaries .
    # def read_orm(self,fields=['name','gender']):
    #     # ret = self.env['school.student'].search([]).read(fields) # return all recordset , use to get ids of all recordset
    #     ret = self.env['school.student'].browse([8]).read(fields)
    #     print("ret::::::::::::::::",ret)

    """#################  READ_GROUP METHOD : ################"""
    # # # there is no need of decorator @api.model or @api.multi in write method
    # #give the list of records in a `list` , grouped by the given `groupby` fields
    # def read_group_orm(self):
    #     ret = self.env['school.student'].read_group(domain=[('student_fees','>','500')], fields=['total_fees:sum'], groupby=['school_id'],orderby='school_id')
    #     print("ret::::::::::::::::",ret) # returns a list of dictionaries with additional metadata like __domain and __context.

    """#################  _READ_GROUP METHOD : ################"""
    # # # there is no need of decorator @api.model or @api.multi in write method

    # # give the list of records in a `list` , grouped by the given `groupby` fields
    # def read_group_orm(self):
    #     ret = self.env['school.student']._read_group(domain=[('total_fees','>','10000')], aggregates=['total_fees:sum'], groupby=['school_id','name'],order='school_id')
    #     print("ret::::::::::::::::",ret) # returns a list of tuples.

    """#################  EXISTS METHOD : ################"""
    # def exists_orm(self):
    #     # sl = self.env['school.student'].search([]) # return all recordset , use to get ids of all recordset
    #     # print(sl) print ids of all recordset
    #     l = [1,2,3,4,8, 9, 10, 11] # this list contains assumed ids of recordset
    #     stud_list = self.env['school.student'].browse(l)
    #     for stud in stud_list:
    #         if stud.exists(): # Returns the subset of records in self , if that exist.
    #             print(stud.id,stud.name)
    #         else:
    #             print("not exist")

    """#################  ENSURE_ONE METHOD : ################"""
    # #  Verify that the current recordset holds a single record.
    # def ensure_one_orm(self):
    #     stud = self.env['school.student'].search([('gender','=',"female")])
    #     print(stud)
    #     if stud.ensure_one():
    #         print(True)
    #     else: # Raises an ValueError if the record set contains more than one record.
    #         raise ValueError("no record found")

    """#################  GET_METADATA METHOD : ################"""
    # # # Read the requested records in self, and return their Metadata as a list of dictionaries .
    # #
    # def get_metadata_orm(self):
    #     # sl = self.env['school.student'].search([]) # return all recordset , use to get ids of all recordset
    #     ret = self.env['school.student'].browse([8]).get_metadata()
    #     print("ret::::::::::::::::",ret)

    """#################  FIELDS_GET_METHOD : ################"""

    # # give the definition of each field records from the database in a dictionaries .
    #
    # def fields_get_orm(self):
    #     # sl = self.env['school.student'].search([]) # return all recordset , use to get ids of all recordset
    #     ret = self.env['school.student'].browse([8]).fields_get()
    #     print("ret::::::::::::::::", ret)

    """#################  FILTERED METHOD : ################"""
    # # give the Filter records based on a condition.
    #
    # def filtered_orm(self):
    #     # sl = self.env['school.student'].search([]) # use to get ids of all recordset
    #     ret = self.env['school.student'].search([]).filtered(lambda x: x.gender == 'male') # return recordset of records
    #     print("ret::::::::::::::::", ret) # print filtered recordset

    """#################  FILTERED_DOMAIN METHOD : ################"""
    # # give the Filter records based on a given Domain.
    #
    # def filtered_domain_orm(self):
    #     # sl = self.env['school.student'].search([]) # use to get ids of all recordset
    #     ret = self.env['school.student'].search([]).filtered_domain([('gender','=','male')]) # return recordset of records
    #     print("ret::::::::::::::::", ret) # print filtered recordset

    """#################  MAPPED METHOD : ################"""
    # # # Apply func to all of its own records and return the result as a list or record (if func returns a record).
    # # In the latter case, the order of the returned records is arbitrary.
    #
    # def mapped_orm(self):
    #                                     # we use search([]) to get ids of all recordset ?? instead of search([]) we can use browse(['id']) for particular record
    #     ret = self.env['school.student'].search([]).mapped(lambda x: x.school_id)  # return recordset of records
    #
    #     # ret = self.env['school.student'].search([]).mapped('name')  # return list of name
    #     # ret = self.env['school.student'].browse([8]).mapped('name')  # return a name
    #     print("ret::::::::::::::::", ret)  # print all recordset
    #     for r in ret:
    #         print("r",r,r.name)



    """#################  SORTED METHOD : ################"""
    # give sorted recordset by given key

    # def sorted_orm(self):
    #     # we use search([]) to get ids of all recordset // instead of search([]) we can use browse(['id']) for particular record
    #     ret = self.env['school.student'].search([]).sorted(key='name', reverse=False) # return sorted recordset by given condition
    #     # ret = self.env['school.student'].search([]).sorted(lambda x: x.name) # we can also use a lambda fun. as key
    #     print("ret::::::::::::::::", ret) # print  sorted recordset
    #     for r in ret:
    #         print("r",r,r.name)

    """#################  GROUPED METHOD : ################"""
    # give grouped recordset by given key
    # def grouped_orm(self):
    #     # we use search([]) to get ids of all recordset // instead of search([]) we can use browse(['id']) for particular record
    #     ret = self.env['school.student'].search([]).grouped(key='id') # return dictionary which contain grouped recordset by given key
    #     # ret = self.env['school.student'].search([]).grouped(lambda x: x.name) # we can also use a lambda fun. as key
    #     print("ret::::::::::::::::", ret) # print  sorted recordset

    ##########################################################################################################
    """ #######################################  OVERRIDE METHODS  ##############################################"""
    ##########################################################################################################

    """#################  OVERRIDE CREATE METHOD : ################"""
    # @api.model
    # def create(self, values): # "self" represents a record set of school.student model
    #     print("Before values",values) # values return in dictionary
    #     print("self",self) # self return in object which is class name
    #     if values.get('gender') == 'male':
    #         values['total_fees'] = 10000
    #         values['name'] = 'Mr.' + values['name']
    #     elif values.get('gender') == 'female':
    #         values['total_fees'] = 5000
    #         values['name'] = 'Mrs.' + values['name']  # this make changes in values of total_fees and name after create
    #     else:
    #         values['total_fees'] = 10000
    #     rtn = super(school_student, self).create(values)
    #     # if values.get('gender') == 'male':
    #     #     rtn.total_fees = 10000
    #     #     rtn['name'] = 'Mr. ' + rtn['name']
    #     # else:
    #     #     rtn.total_fees = 5000 # this also make changes in rtn of total_fees after create , but this syntax is used after super method.
    #     print("After values",values) # this make changes in values of total_fees after create but it cant be seen in console because of add in id
    #     print("rtn",rtn) # rtn return in object which is class
    #     return rtn

    """#################  OVERRIDE WRITE(UPDATE) METHOD : ################"""

    # there is no need of decorator @api.model or @api.multi in write method
    # def write(self, vals):   # "self" represents a record set of school.student model
    #     vals['total_fees'] = 12000  # this make changes in values of total_fees after WRITE / UPDATE
    #     rtn = super(school_student, self).write(vals)  # this return "True" or "False"
    #     print(self,rtn,vals)
    #     return rtn # this return "True" or "False"


    """################  OVERRIDE COPY(DUPlICATE) METHOD : ################"""
    @api.returns('self',lambda value: value.id) # optional to use without this api, method works same
    def copy(self,default= None): # we can use here "default = None" // or // "default = {}" (give empty dictionary)
        default = dict(default or {}) # if we use "default = None"  then this is must for set Dictionary as default
        # default['gender'] = 'male'
        print("default",default) # this give default value
        print("self",self) # this give current record
        rtn = super(school_student, self).copy(default= default) # this make NEW copied record
        print("rtn",rtn) # this print NEW copied record
        return rtn


    """#################  OVERRIDE UNLINK (DELETE) METHOD : ################"""
    # def unlink(self): # "self" represents a record set of school.student model
    #     print("self",self) # this print current record
    #     for stu in self:
    #         if stu.active:
    #             raise UserError(f'Cannot delete Active record of student {stu.name} with {stu.total_fees} fees')
    #     rtn = super(school_student, self).unlink() # this return "True" or "False"
    #     print("rtn",rtn) # this print "True" or "False"
    #     return rtn

    """#################  default_get() METHOD : ################"""
    # @api.model
    # def default_get(self, fields_list): # 2nd parameter is list of fields which contains all fields of model in LIST
    #     print("fields_list",fields_list)
    #     rtn = super(school_student, self).default_get(fields_list) # this return dictionary which contains default values of model's fields
    #     # rtn['gender'] = 'male'
    #
    #     print("rtn",rtn)
    #     return rtn # this return dictionary which contains default values of model's fields


#######################################################################################################################
    """########################################## ACTIONS : ##########################################################"""
#######################################################################################################################

    """################# URL ACTION : ################"""

    # Allow opening a URL (website/web page) via an Odoo action. Can be customized via two fields:
    # url : the address to open when activating the action
    # "target = new" use for wiz. open in new page
    # "target = self//current" use for wiz. open in current page
    # "target = download" redirects to a download URL

    def url_action(self):
        return{
            'type': 'ir.actions.act_url',
            'url': 'https://www.google.com',
            'target': 'new'
        }
    """################# SERVER ACTION : ################"""
    # Purpose: Execute server-side logic (e.g., Python code, record creation).
    # Execution Options:
        # Execute Python Code: Runs Python code.
        # Create a new Record: Creates a new record with specified values.
        # Write on a Record: Updates a record with new values.
        # Execute several actions: Triggers multiple server actions.
    @api.model
    def server_code(self):
        ids = self.search([])
        print(ids)
        if ids:
            for i in ids:
                if i.total_fees <= 5000 and i.gender == 'male':
                    print(i.name, i.total_fees)

    """################# CLIENT ACTION : ################"""

    def client_action(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'target': 'fullscreen',
            'params': {
                'type': 'success',
                'message': _("client_action success"),
            }
        }

    """################# AUTOMATED ACTION : ################"""
    # Purpose: Manages actions that are automatically triggered based on a predefined schedule.

    def send_reminder(self):
        students = self.search([('gender', '=', 'female')])  # Fetch all students with virtual_class = True
        for stu in students:
            print("calling send reminder for", stu.name)
            raise UserError(f'Send Reminder for {stu.name} with {stu.total_fees} fees')
#######################################################################################################################
    """##############################################################################################################"""
#######################################################################################################################

"""################# DIFFERENT MODEL INHERITANCE : ################"""

# Inherit from another model (School Model/ Folder)
# First, add the inherited model in 'depends' of __manifest__.py.
# Create the inherited model class in models.py.
# Create proper views for this inherited model in views.xml of this module.
# Update your module to apply the changes.
# No need for any access rights for this class.
class SchoolProfile(models.Model):
    _inherit = 'school.profile'

    full_name = fields.Char(string="Full Name")

    """################  One2many field : ################"""

    # Connects one record from the current model to multiple records in another model. Useful for lists of related items.

    """field_name = fields.One2many('related.model', 'related_field', string="Field Label" )"""
    # 'related.model' / comoodel_name : The name of the related model (e.g., 'school.student').
    # 'related_field' / inverse_name : The field in the related model that establishes the relationship (e.g., 'school_id').
    # 'string' / "Field Label" : An optional label for the field (used in forms and views).

    school_list = fields.One2many('school.student' , 'school_id' , string="Student List" , required=True )
    # It links records from the current model ('school') to records in the 'school.student' model.
    # The relationship is based on the 'school_id' field in the 'school.student' model.



    """#################  NAME_SEARCH METHOD : ################"""
    # To search for records with a display name that matches a given domain and conditions.
    # The search is performed on the 'School_list' field of the "school_student" model.
    # Returns a list of tuples , [ (id, display_name),..].
    # need '@api.model' decorator

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     if name: # if ANY word written in search box then search it from school_list with this condition
    #         rec = self.search(domain=['|', '|', '|', ('name', operator, name), ('email', operator, name),
    #                                   ('school_type', operator, name), ('school_number', operator, name)],
    #                           limit=limit).name_get()
    #         print("rec", rec)  # Print a list of tuples
    #         return rec  # Returns a list of tuples
    #     rrr = self.search(args, limit=limit).name_get() # if nothing written in search box then SHOW ALL School from school_list WITHOUT any condition
    #     # rrr = super(SchoolProfile, self).name_search(name=name, args=args, operator=operator, limit=limit)
    #     print("rrr", rrr)  # Print a list of tuples
    #     return rrr  # Returns a list of tuples

    """#################  _NAME_SEARCH METHOD : ################"""
    # Commonly used for providing suggestions in relational fields
    # Returns the Query object or IDs of matching records.
    # need @api.model of any decorator
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100,order=None):
        args = args or []
        domain = []
        print("name",name)
        print("args",args)
        print("operator",operator)
        print("limit",limit)
        if name: # # if ANY word written in search box then search it from school_list with this condition
            domain = ['|','|','|',('name', operator, name), ('email', operator, name), ('school_type', operator, name),('school_number', operator, name)]
        rrr = self._search(domain+args, limit=limit,order=order ) # if nothing written in search box then SHOW ALL School from school_list WITHOUT any condition
        print("rrr",rrr)
        return rrr  # Returns the Query object or IDs of matching records.


#######################################################################################################################
"""#######################################################################################################################"""
#######################################################################################################################

from odoo import api, fields, models

class Hobby(models.Model):
    _name = 'hobby'
    _description = 'Hobby Page'

    name = fields.Char("Hobbies")
    selection = fields.Selection([('one', 'One'), ('two', 'Two')], string="Selection")
    partner_name = fields.Char("Partner Name")
    partner2_name = fields.Char("Partner-2 Name")




    """#################  SQL CONSTRAINTS : ################"""
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Hobby names must be unique!')
    ]


#######################################################################################################################
"""############################################### INHERITANCE ###########################################################"""
#######################################################################################################################

"""################# CLASSICAL // 2 DIFFERENT MODEL INHERITANCE : ################"""

# Inherit from another model (Hospital Model/ Folder)
# It allows extending and overriding.
# First, add the inherited model in 'depends' of __manifest__.py.
# Create the inherited model class in models.py.
# Create proper views for this inherited model in views.xml of this module.
# Update your module to apply the changes.
# No need for any access rights for this class.

class HospitalPatientInherited(models.Model):
    _inherit = 'hospital.patient'

    selection = fields.Selection([('one', 'One'), ('two', 'Two')], string="Selection")




"""################# DELEGATION INHERITANCE : ################"""

# we use '_inheritS'
# used to Inherit for current model (School Model/ Folder) Using Dictionary
# Dictionary should be in format: {'KEY = inherited model name': 'VALUE = name of many2one field in parent model'}
# Establishing a Many-to-one relationship.
# Many-to-one relationship is based on the inherited 'sports' model.
# its required to give access rights for this class.
# no need to add the inherited module in 'depends' of __manifest__.py.
# no need to Create proper views for this inherited model in views of this module
# just add fields in xml view of inherited model as normally added.
# Update your module to apply the changes.

class Sports(models.Model):
    _name = 'sports'

    name = fields.Char("Sports Name")
    sport_type = fields.Selection([('indore', 'Indore'), ('outdore', 'Outdore')], string="Selection")

class StudentEquipment(models.Model):
    _name = 'student.equipment'  # model name
    _inherits = {'sports': 'sports_id'}  # {'KEY = inherited model name': 'VALUE = name of many2one field in parent model'}

    sports_id = fields.Many2one('sports', string="Sports Name")
    eq_name = fields.Char("Equipment name")
