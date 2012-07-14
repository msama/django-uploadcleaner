'''
Created on Jul 14, 2012

@author: Michele Sama (m.sama@puzzledev.com)
'''
import os
import datetime
from zipfile import ZipFile

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from uploadcleaner.utils import linked_files_from_all_models, files_at_path
from django.db.utils import DEFAULT_DB_ALIAS


def _log_file_name(model_instance, filename):
    #f_name, ext = os.path.splitext(filename)
    new_file = "%s/%s/%s" % (
            model_instance._meta.module_name,
            model_instance.timestamp,
            filename)
    return (new_file)

def _backup_file_name(model_instance, filename):
    #f_name, ext = os.path.splitext(filename)
    new_file = "%s/%s/%s" % (
            model_instance._meta.module_name,
            model_instance.timestamp,
            filename)
    return (new_file)


class UploadCleanerLogManager(models.Manager):
    
    def do_clean(self, backup = True, dryrun = False):
        """ Perform the cleaning operation.
        """
        files_on_filesystem = self.files_from_upload_paths()
        files_on_db =  linked_files_from_all_models()
        
        obsolete_files = self.filter_linked_files(
                files_on_filesystem, files_on_db)
        
        log_instance = self.create(
                dryrun = dryrun)
        
        # Create backup
        if backup:        
            self.create_backup(obsolete_files, log_instance)
        
        if dryrun:
            self.dryrun(obsolete_files)
        else:       
            self.delete_obsolete_files(obsolete_files, log_instance)
        log_instance.save()
        return log_instance
        
    
    def files_from_upload_paths(self):
        """ Creates a list with all the files in the
            defined upload folders.
        """
        if hasattr(settings, 'MEDIA_FOLDER_LIST'):
            print("Fetching files from %s" %
                  settings.MEDIA_FOLDER_LIST)
            upload_paths = settings.MEDIA_FOLDER_LIST
        else:
            print("settings.MEDIA_FOLDER_LIST is not set.")
            print("Fetching files from %s" %
                  settings.MEDIA_ROOT)
            upload_paths = (settings.MEDIA_ROOT,)
            
        files_on_filesystem = []
        for folder in upload_paths:
            files_on_filesystem += files_at_path(folder)
        return files_on_filesystem


    def filter_linked_files(self,
            files_on_filesystem, files_on_db):
        """ Given the list of all the files in the upload path
            filter those files which are linked by the database
            and those which are in the log directory.
        """
        return [x 
                for x in files_on_filesystem
                if x not in files_on_db]
        
            
    def create_backup(self, files, instance):
        backup_filename = _backup_file_name(instance, "backup.zip")
        backup = ZipFile(backup_filename,"w")
        for filename in files:
            backup.write(filename)
        backup.close()
        instance.backup_file.name = backup_filename


    def dryrun(self, files):
        """ Print the list of obsolete files without
            deleting them.
        """
        for filename in files:
            print "dryrun: %s" % filename  


    def delete_obsolete_files(self, files, instance):
        """ Delete all the obsolete files and save
            their name in a log file.
        """
        log_filename = os.path.join(
                self.log_folder + 
                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +
                ".log")
        
        log = open(log_filename, "w")
        for filename in files:
            log_string = "removing: %s" % filename
            print(log_string)
            log.write(log_string + "\n")
            os.remove(file)
        log.close()
        instance.log_file.name = log_filename


class UploadCleanerLog(models.Model):
    """ Stores the log of each clean.
    """
    timestamp = models.DateTimeField(
            auto_add_now = True,
            verbose_name = _("Timestamp"),
            help_text = _("When this clean up was performed."))

    dryrun = models.BooleanField(
            blank = True,
            null = True,
            verbose_name = _("Dry-run"),
            help_text = _("Performs a dry run"))
    
    log_file = models.FileField(
            blank = True,
            null = True,
            upload_to = _log_file_name, 
            verbose_name = _("Log file"),
            help_text = _("The log file."))
    
    backup_file = models.FileField(
            blank = True,
            null = True,
            upload_to = _backup_file_name, 
            verbose_name = _("Backup file"),
            help_text = _("The backup file."))
    
    objects = UploadCleanerLogManager()
    
    class Meta:
        ordering = ('timestamp',)
        verbose_name = _("Upload cleaner log")
        verbose_name_plural = _("Upload cleaner log")
        
    def delete(self, using = DEFAULT_DB_ALIAS):
        self.log_file.delete();
        self.backup_file.delete();
        super(UploadCleanerLog, self).delete(using)