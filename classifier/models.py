'''
Created on Feb 10, 2012

@author: Dannie
'''

from django.db import models
from json.decoder import JSONDecoder
import hashlib
import logging
from django.utils.translation import ugettext_lazy as _


class ClassifierCategory(models.Model):
    categoryName = models.CharField(max_length=50, verbose_name=_(u"Name"))
    yes = models.BooleanField(default=False, verbose_name=_(u"Positive"))
    
    class Meta:
        unique_together = (('categoryName', 'yes'),)
        verbose_name = _(u"classifier category")
        verbose_name_plural = _(u"classifier categories")
    
    def __str__(self):
        return self.categoryName + "-" + str(self.yes)
    
    
    @staticmethod
    def getCategoriesByIds(ids):
        logger = logging.getLogger("DocumentCategory.getCategoriesByIds")
        
        categories = None
        try :
            categories = ClassifierCategory.objects.filter(id__in=ids)
            
        except Exception, ex :
            logger.info("Failed to retrieve the classifier category by ids: %s" + str(ex))
            
        return categories
    
    @staticmethod
    def getCategoryCreate(categoryName=None, yes=False):
        logger = logging.getLogger("DocumentCategory.getCategory")
        category = None
        try :
            category = ClassifierCategory.objects.get_or_create(categoryName=categoryName, yes=yes)
        except Exception, ex :
            logger.exception("Failed to create the new classifier category: %s" % str(ex))
            
        return category
    
    '''
    Retrieves all categories
    '''
    @staticmethod 
    def getAllCategories():
        logger = logging.getLogger("DocumentCategory.getAllTrainedCategories")
        
        categories = None
        try :
            categories = ClassifierCategory.objects.all()
        except Exception:
            logger.exception("Failed to retrieve all the categories")
        return categories
    
'''
Document that we use to train the classifier, stored for easy 
retrieval later on.
'''
class Document(models.Model):
    corpus = models.TextField(default=" ", verbose_name=_(u"Corpus"))
    corpusHash = models.CharField(max_length=60, verbose_name=_(u"Hash"))

    class Meta:
        verbose_name = _(u"classifier document")
        verbose_name_plural = _(u"classifier documents")

def __str__(self):
        return str(self.id) + " " + self.corpus[:150] 

    @staticmethod
    def getHash(corpus):
        corpusHash = hashlib.md5()
        corpusHash.update(corpus)
        return corpusHash.hexdigest()

    def save(self, *args, **kwargs):
        if self.corpus :
            self.corpusHash = Document.getHash(self.corpus)
            
        return super(Document, self).save(*args, **kwargs)
    
    '''
    looks up a document given a corpus
    '''
    @staticmethod
    def getDocumentByCorpus(corpus, create=False):
        corpusHash = Document.getHash(corpus)
        documents = Document.objects.filter(corpusHash=corpusHash)
        
        foundDocument = None
        
        if documents and len(documents) > 0 :
            for document in documents :
                foundDocument = document
                break
        elif create :
            foundDocument = Document(corpus=corpus)
            foundDocument.save()
                
        return foundDocument
    
    
    @staticmethod
    def removeDocumentByCorpus(corpus):
        logger = logging.getLogger("Document.removeDocumentByCorpus")
        
        document = Document.getDocumentByCorpus(corpus)
        success = False
        if document :
            try :
                document.delete()
                success = True
            except Exception, ex :
                logger.exception("Failed to remove documnet: " + str(ex))
        return success
    
    
    def getCategories(self, yes = True):
        return ClassifierCategory.objects.filter(documentcategory__document=self, yes=yes)
        
    
'''
Mapping of feature to all the category counts.
Feature-category counts are separated out by parent categories for classification
optimizations.  Therefore, when classifying we don't need to retrieve a massive list of 
all the categories when we're only concerned about a particular level or branch of the 
taxonomy tree. 
'''
class FeatureCounts(models.Model):
    featureName = models.CharField(max_length=100, unique=True)
    countData = models.TextField()
    
'''
Mapping of document to all it's category counts
'''
class DocumentCategoryCounts(models.Model):
    document = models.ForeignKey(Document, unique=True)
    countData = models.TextField()
    
    @staticmethod
    def getCategoriesForDocument(document):
        logger = logging.getLogger("DocumentCategory.getCategoriesForDocument")
        
        categories = None
        try :
            documentCount = DocumentCategoryCounts.objects.get(document=document)
            jsonDecoder = JSONDecoder()
            categories = jsonDecoder.decode(documentCount.countData)
            categories = ClassifierCategory.getCategoriesByIds(categories.keys())
        except Exception, ex :
            logger.exception("Failed to retrieve the categories for the document" + str(ex))
            
        return categories
    
'''
An index of the number of documents classified for a particular category.
Purely for classification optimization.
'''
class CategoryDocumentCountIndex(models.Model):
    indexId = models.IntegerField(unique=True, db_index=True)
    countData = models.TextField()
    
    @staticmethod
    def getCountIndex():
        index,_ = CategoryDocumentCountIndex.objects.get_or_create(indexId=0)
        return index
    
    
