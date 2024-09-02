from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location='media/')

class Department(models.Model):
    dep_id = models.AutoField(primary_key=True)
    dep_name = models.CharField(max_length=255)
    dep_abbr = models.CharField(max_length=7, blank=True, null=True)
    is_active = models.CharField(max_length=1,default='Y')

    class Meta:
        managed = False
        db_table = 'department'

class Staff(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(unique=True,max_length=255)
    password = models.CharField(max_length=255)
    contact = models.CharField(max_length=10)
    role = models.CharField(max_length=2)
    isactive = models.CharField(db_column='isActive', max_length=1,default='Y')  # Field name made lowercase.
    picture = models.ImageField(upload_to='profile/',storage=fs,null=True,blank=True)
    street_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pin = models.CharField(max_length=6)
    state = models.CharField(max_length=50)
    is_admin = models.CharField(max_length=1)
    joining_date = models.DateField()
    leaving_date = models.DateField(blank=True, null=True)
    dep = models.ForeignKey('Department', on_delete=models.PROTECT, blank=True, null=True)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('self', on_delete=models.PROTECT, db_column='created_by', blank=True, null=True)
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('self',on_delete= models.PROTECT, db_column='updated_by', related_name='staff_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'staff'

class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_name = models.CharField(max_length=100)
    program_abbr = models.CharField(max_length=7, blank=True, null=True)
    is_active = models.CharField(max_length=1,default='Y')
    dep = models.ForeignKey('Department', on_delete=models.PROTECT)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='created_by')
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='updated_by', related_name='program_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'program'

class Batch(models.Model):
    batch_id = models.AutoField(primary_key=True)
    start_year=  models.PositiveIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(9999)
        ]
    )

    duration = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(9)
        ]
    )
    program = models.ForeignKey(Program, on_delete=models.PROTECT)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='created_by')
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff',  on_delete=models.PROTECT, db_column='updated_by', related_name='batch_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'batch'

class Division(models.Model):
    div_id = models.AutoField(primary_key=True)
    div_name = models.CharField(max_length=1)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='created_by')
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='updated_by', related_name='division_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'division'

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    enrolment_no = models.CharField(unique=True, max_length=15)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    div = models.ForeignKey(Division,on_delete=models.PROTECT)
    email = models.CharField(unique=True,max_length=255)
    password = models.CharField(max_length=255)
    contact = models.CharField(max_length=10)
    picture = models.ImageField(upload_to='profile/',storage=fs,null=True,blank=True)
    street_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pin = models.CharField(max_length=6)
    state = models.CharField(max_length=50)
    lib_barcode = models.CharField(max_length=500)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('Staff',on_delete=models.PROTECT, db_column='created_by')
    isactive = models.CharField(db_column='isActive', max_length=1,default='Y')
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff',on_delete=models.PROTECT, db_column='updated_by', related_name='student_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student'

    def save(self, *args, **kwargs):
        # Update Batch, Program, and Department based on the associated Division
        if self.div:
            self.batch = self.div.batch
            if self.batch:
                self.program = self.batch.program
                if self.program:
                    self.dep_id = self.program.dep
        
        # Call the parent class's save method to save the changes
        super().save(*args, **kwargs)
    
class Alumni(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    enrolment_no = models.CharField(unique=True, max_length=15)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    contact = models.CharField(max_length=10)
    picture = models.ImageField(upload_to='profile/',storage=fs,null=True,blank=True)
    street_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pin = models.CharField(max_length=6)
    state = models.CharField(max_length=50)
    lib_barcode = models.CharField(max_length=500)
    div = models.ForeignKey('Division', on_delete=models.PROTECT)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='created_by')
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='updated_by', related_name='alumni_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Alumni'

class Guard(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    isactive = models.CharField(db_column='isActive', max_length=1,default='Y')  # Field name made lowercase.
    contact = models.CharField(max_length=10)
    picture = models.ImageField(upload_to='profile/',storage=fs,null=True,blank=True)
    street_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pin = models.CharField(max_length=6)
    state = models.CharField(max_length=50)
    joining_date = models.DateField()
    leaving_date = models.DateField(blank=True, null=True)
    working_gate = models.CharField(max_length=1)
    dep = models.ForeignKey('Department', on_delete=models.PROTECT)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='created_by')
    update_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='updated_by', related_name='guard_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Guard'

class Discussion(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_title = models.CharField(max_length=100)
    post_content = models.TextField()
    post_date = models.DateField(auto_now_add=True)
    posted_by = models.ForeignKey('Alumni', on_delete=models.PROTECT, db_column='posted_by')
    isapproved = models.CharField(db_column='isApproved', max_length=1,default='P')  # Field name made lowercase.
    approved_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='approved_by', blank=True, null=True)
    approved_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discussion'

class DocMaster(models.Model):
    docm_id = models.AutoField(db_column='docM_id', primary_key=True)  # Field name made lowercase.
    doc_name = models.CharField(max_length=255)
    isoffered = models.CharField(db_column='isOffered', max_length=1)  # Field name made lowercase.
    offeredto = models.CharField(db_column='offeredTo', max_length=1)  # Field name made lowercase.
    created_on = models.DateTimeField()
    created_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='created_by')
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='updated_by', related_name='docmaster_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doc_master'

class DocRequest(models.Model):
    doc_id = models.AutoField(primary_key=True)
    docm = models.ForeignKey(DocMaster, on_delete=models.PROTECT, db_column='docM_id')  # Field name made lowercase.
    request_time = models.DateTimeField(auto_now_add=True)

    # Fetch requester_id using the user_id passed from flutter
    requester_id = models.CharField(max_length=15)

    # Role provided from flutter
    requester_role = models.CharField(max_length=7)
    
    # Use registered name
    # full_name = models.CharField(max_length=100)
    purpose = models.CharField(max_length=255)
    isapproved = models.CharField(db_column='isApproved', max_length=1,default='P')  # Field name made lowercase.
    doc_file = models.FileField(upload_to='pdfs/',blank=True,null=True)
    no_of_copies = models.CharField(max_length=2)
    additional_instructions = models.CharField(max_length=300,blank=True,null=True)
    approved_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='approved_by', blank=True, null=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey('Staff', on_delete=models.PROTECT, db_column='updated_by', related_name='docrequest_updated_by_set', blank=True, null=True)
    updated_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doc_request'


