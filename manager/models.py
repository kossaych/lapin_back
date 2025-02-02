from typing import Any
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save

from rest_framework import status 
from rest_framework.response import Response

from accounts.models import User,GeneralConfig
from django.conf import settings
from .untils import *

import uuid
import shutil
import time
#import pandas as pd 

base_path=settings.BASE_DIR
aujourdhui_date=str(timezone.now().year)+"-"+str(timezone.now().month)+'-'+str(timezone.now().day)

def upload_to(instance,filename):
    extention = filename.split('.')[-1]
    filename = str(uuid.uuid4())+"."+(extention)
    return '/'.join([str(instance.cage),filename])










class Race(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    race=models.CharField(max_length=200,unique=True)
    Moyenne_poid_malle=models.IntegerField(default=3500)
    Moyenne_poid_femalle=models.IntegerField(default=3000)
    Moyenne_production_annuelle=models.IntegerField(default=50)
    Moyenne_poid_2moi=models.IntegerField(default=3500)
    Moyenne_production_par_accouplement=models.IntegerField(default=50)
    def __str__(self):
         return self.race
    


class Maladie(models.Model):
    TYPES_MALADIES_LAPINS=[   
                        ("Les_maladies_dermatologiques","Les maladies dermatologiques"),
                        ("Les_maladies_respiratoires","Les maladies respiratoires"),
                        ("Les_maladies_digestives","Les maladies digestives"),
                        ("Les_maladies_de_l'appareil_urinaire","Les maladies de l'appareil urinaire"),
                        ("La_maladie_hémorragique_du_lapin","La maladie hémorragique du lapin"),
                        ("Les_tumeurs","Les tumeurs"),
    ]

    maladie=models.CharField(max_length=200,default='____')
    type=models.CharField(choices=TYPES_MALADIES_LAPINS,max_length=200,default='__')
    def __str__(self):
        return str(self.maladie)







# general Vaccin Fields
class Vaccin(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True , blank=True)
    #lapin=models.ForeignKey(LapinProduction,on_delete=models.CASCADE ,null=True , blank=True)
    date_vaccin=models.DateField(null=True,blank=True)
    nom=models.CharField(max_length=50,null=True,blank=True)
    prix=models.IntegerField(null=True,blank=True)
    maladie=models.ForeignKey(Maladie,on_delete=models.CASCADE,null=True , blank=True)
    #def __str__(self):
    #        return str(self.nom+" contre "+self.maladie)  
    class Meta :
        abstract = True # Use this when the parent class contains common fields and the parent class table is not desirable.
# general poid fields
class Poid(models.Model):
    date_mesure=models.DateField(null=True,blank=True)
    valeur=models.IntegerField(null=True,blank=True)   
    class Meta :
        abstract = True # Use this when the parent class contains common fields and the parent class table is not desirable.

# general Lapin Fields

class Lapin(models.Model):
    
    create_at=models.DateField(default=timezone.now)
    img=models.ImageField(upload_to = upload_to ,null=True , blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE ,null=True,blank=True)
    
    cage=models.CharField(max_length=50,null=True,blank=True)
    
    race = models.ForeignKey(Race,on_delete=models.CASCADE ,null=True,blank=True)
    
    #date_naissance=models.DateField(default=timezone.now)
    state=models.CharField(max_length=50, default='production',choices=[("mort","mort"),("vendue","vendue"),("production","production")])
    date_mort=models.DateField(null=True,blank=True)
    prix=models.IntegerField(null=True,blank=True)
    date_vent=models.DateField(null=True,blank=True)  

    #supremer la femalle et ca photo
    def delete(self,*args, **kwargs):
        try:
            shutil.rmtree((base_path+'/media/'+str(self.img)[:str(self.img).index('/')]))
        except :
            pass
        super().delete(*args, **kwargs)


    # vent la femalle
    def vent(self,prix,date_vent):
            if self.state == "production": 
                try :
                    prix=int(prix)
                except :
                    return Response("prix invalide",status=status.HTTP_400_BAD_REQUEST)
                if prix > 0 :                              
                    self.prix = prix  
                else:return Response("prix invalide",status=status.HTTP_400_BAD_REQUEST)                                                   
                
                try :
                    age_lapin=age(self.date_naissance)
                    vendé_depuis=age(date_vent)
                except:
                    return Response("date de vent invalide",status=status.HTTP_400_BAD_REQUEST)  
               
               
                if vendé_depuis >= 0 and age_lapin-vendé_depuis >= 0 :   
                        self.date_vent = date_vent
                else : return Response("date de vent invalide",status=status.HTTP_400_BAD_REQUEST)  
                

                self.state='vendue'
                self.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            return Response("invalid request",status=status.HTTP_400_BAD_REQUEST) 
    def mort (self,date_mort):
        if self.state == "production":
            try :
                age_lapin=age(self.date_naissance)
                mort_depuis=age(date_mort)
            except:
                return Response("date de mort invalide",status=status.HTTP_400_BAD_REQUEST) 
            if mort_depuis >= 0 and age_lapin-mort_depuis>=0:   
                    self.date_mort=date_mort
            else : return Response("date de mort invalide",status=status.HTTP_400_BAD_REQUEST) 
            
            self.state='mort'
            self.save() 
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response("invalid request",status=status.HTTP_400_BAD_REQUEST) 

    def age (self) : 
          return age_handler(self.date_naissance)
    def __str__(self):
            return str(self.cage)
    class Meta:
        abstract = True # Use this when the parent class contains common fields and the parent class table is not desirable.



# pour enregister chaque changement de prix des aliments
class PrixAliments(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True ,blank=True)
    date_changement=models.DateField(null=True,blank=True)
    prix=models.IntegerField(null=True,blank=True)   
    # retourner le dernier date de changement de prix des alimants anvant un date précie
    @ classmethod
    def le_plus_proche_date_a_gauche(cls,date,user):
        coup_cons_choisie={}
        for coup_cons in cls.objects.filter(user=user) :
            if coup_cons_choisie=={}:
                coup_cons_choisie=coup_cons
            else:
                if age(coup_cons.date_changement)>=age(date) and age(coup_cons.date_changement)-age(date)<age(coup_cons_choisie.date_changement)-age(date):
                    coup_cons_choisie=coup_cons
        
        return coup_cons_choisie
            
class Malle(Lapin):
    acouplements = models.ManyToManyField('Femalle', through="Accouplement")
    date_naissance=models.DateField(default=timezone.now) 
    @classmethod
    def __virif_cage(cls,cage,user):
        for femalle in cls.objects.filter(user=user):
                    if cage == int((femalle.cage)[1:]):
                        return True
        return False      
    @classmethod          
    def cage_vide (cls,user):
        for cage in range(1,len(cls.objects.filter(user=user))+1):
                if not cls.__virif_cage(cage,user):
                    return 'M'+str(cage)
        max=len(cls.objects.filter(user=user))
        return 'M'+str(max+1)
    
    def mesures_poids(self):
        poids = PoidMalle.objects.filter(malle=self) 
        return  [   {
                        'malle':str(self.id),
                        'valeur':str(poid.valeur),
                        'date_mesure':str(poid.date_mesure),
                    } 
                    for poid in poids 
                ]  
    
class Femalle(Lapin):
    acouplements = models.ManyToManyField(Malle, through="Accouplement")
    date_naissance=models.DateField(default=timezone.now)
    @classmethod
    # une fonction pour verifier la posibilité de l'utilisation d'un num de cage return bool
    def __virif_cage(cls,cage,user):
        for femalle in cls.objects.filter(user=user):
                    if cage == int((femalle.cage)[1:]):
                        return True
        return False      
    @classmethod
    #return un cage vide pour la criation d'une nouvelle femalle       
    def cage_vide (cls,user):
        for cage in range(1,len(cls.objects.filter(user=user))+1):
                if not cls.__virif_cage(cage,user):
                    return 'F'+str(cage)
        max=len(cls.objects.filter(user=user))
        return 'F'+str(max+1)
    
    def dernier_groupe_production(self):
            date = ""
            dernier_groupe = {}
            groupes = GroupeProduction.objects.filter(acouplement__mère = self )  
            print(list(groupes))
            for groupe in groupes:
               # if groupe.acouplement.mère.id == self.id:
                        if date == "":
                            date = groupe.date_naissance
                            dernier_groupe = groupe
                        elif age(groupe.date_naissance) < age(date):
                            date = groupe.date_naissance
                            dernier_groupe = groupe
            if dernier_groupe == {}:
                return False # False sig que la femalle n"a pas encore des groupe
            else :
                return dernier_groupe  
            



     # retourner True si la femalle est nourice dans un jour précie sinon False
    # virifier si la femalle nourice ou nom  return bool
    def nourice(self,date_jour) :  
        for groupe in GroupeProduction.objects.all():
            if groupe.acouplement.mère.id==self:
                if groupe.date_souvrage ==None:
                    if age(groupe.date_naissance)-age(date_jour)>=0: # le calcule basé sur la diférence des jour entre le date de naissance et le date précie 
                        return True
                else :
                    if age(groupe.date_souvrage)-age(date_jour) < 0 and age(groupe.date_naissance)-age(date_jour)>=0: # le calcule basé sur la diférence des jour entre le date de naissance et le date précie     
                        return True

        return False
    #retourner True si la femalle est enciente dans un jour précie sinon False
    def enceinte(self,date_jour):
        if age(date_jour)>=0: # pour virifier que le date est passé
            for acouplement in Accouplement.objects.filter(mère=self):
                if 33>=age(str(acouplement.date_acouplage))-age(str(date_jour))>=0: # la différence entre l'age du date d'acouplage et l'age du date cherché doit etre positive et inferieur a 33 pour indiquer que le date demander et dans le plage (range) d'accouplement
                    if acouplement.test=="non_vérifié" or acouplement.test=="enciente": # pour assurer que la femalle est effectivement enciente   
                        if acouplement.state== "avant_naissance"  :
                            return True
                        else:    
                            if age(GroupeProduction.objects.get(acouplement=acouplement).date_naissance)-age(str(date_jour))<0: # pour assurer que la fonction return True meme si l'acouplement est déja aprés la naissance (et ca se fait avec une verificatinon par le date de naissance le date demander doit etre avant la date de naissance)
                                return True
                    else :
                        if age(str(date_jour))>=age(str(acouplement.date_test)):
                            return True        

            return False
        return False    
    #retourner le totale de consomation pandent la periode de date initiale jusqu'a le date finale
    def cons(self,initial_date,final_date):
        cons=0
        if (age(final_date)-age(initial_date))<=0 and age(final_date)>=0:
            for jour in list_dates(initial_date,final_date):
                if self.enceinte(jour) and self.nourice(jour) :
                    cons=cons+500
                elif self.enceinte(jour):
                    cons=cons+250
                elif self.nourice(jour) :
                    cons=cons+300
                else:
                    cons=cons+150
        return cons
    
    def mesures_poids(self):  
        mesures_poid = PoidFemalle.objects.filter(femalle=self)     
        for poid in mesures_poid :
                print(poid)
                yield {
                      
                    'valeur': str(poid.valeur), 
                    'date_mesure': str(poid.date_mesure)

                }

    def est_acouplet(self):
            
            for acc in Accouplement.objects.filter(mère=self,state="avant_naissance"):
                if (age(acc.date_acouplage)<=35 and (acc.test=="enceinte" or acc.test=="non_vérifié")):
                    return True
            



            self.acouplements.all()
            return False
    
    
    
    def statistique(self):
        # Calculate statistics
        statistiques = {}

        try:
            # Retrieve the latest group production associated with the Femalle
            dernier_groupe_production = self.dernier_groupe_production()
            # Calculate the total production, total mortality, and total mortality at birth
            statistiques['TP'] = dernier_groupe_production.nb_lapins_nées
            statistiques['TM'] = dernier_groupe_production.totale_mortalité_groupe()
            statistiques['TMN'] = dernier_groupe_production.nb_lapins_mortes_naissances
            # Calculate the net production (total production minus total mortality)
            statistiques['TPnet'] = statistiques['TP'] - statistiques['TM']
            statistiques['dernière_groupe'] = dernier_groupe_production.id
        except:
            # If an error occurs, set the statistics values to zero and an empty dictionary
            statistiques['TP'] = 0
            statistiques['TM'] = 0
            statistiques['TMN'] = 0
            statistiques['TPnet'] = 0
            statistiques['dernière_groupe'] = {}

        # Calculate consumption statistics
        cons_moi = self.cons(age_revers(30), aujourdhui_date) / 1000
        cons_aujourdhui = self.cons(age_revers(0), aujourdhui_date) / 1000
        general_config = GeneralConfig.objects.get(user=self.user)
        coup_cons_moi = cons_moi * int(general_config.coup_alimentation) / 1000
        coup_cons_aujourdhui = cons_aujourdhui * int(general_config.coup_alimentation) / 1000

        # Add consumption statistics to the 'statistiques' dictionary
        statistiques['cons_moi'] = str(cons_moi) + ' kg'
        statistiques['cons_aujourdhui'] = str(cons_aujourdhui) + ' kg'
        statistiques['coup_cons_moi'] = str(coup_cons_moi) + ' dt'
        statistiques['coup_cons_aujourdhui'] = str(coup_cons_aujourdhui) + ' dt'
        return statistiques

    def __str__(self):
            return str(self.cage)

#production     
class Accouplement(models.Model):
    TEST_ACOUPLAGE =[
            ('pas_enceinte','pas enceinte'),
            ('enceinte','enceinte'),
            ('non_vérifié','non vérifié'),
            ('fausse_couche','fausse-couche')
    ]
    STATE_ACOUPLAGE =[
            ('avant_naissance','avant_naissance'),
            ('aprés_naissance','aprés_naissance'),
    ]
    
    père=models.ForeignKey(Malle,on_delete=models.CASCADE,null=True , blank=True)
    mère=models.ForeignKey(Femalle,on_delete=models.CASCADE,null=True , blank=True)
    
    create_at=models.DateField(default=timezone.now)
    num=models.CharField(max_length=50,null=True,blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True , blank=True)

    date_acouplage=models.DateField(default=timezone.now)
    date_fausse_couche=models.DateField(null=True , blank=True)
    date_test=models.DateField(null=True , blank=True)
    test=models.CharField(choices=TEST_ACOUPLAGE ,max_length=200,default='non_vérifié')
    state=models.CharField(choices=STATE_ACOUPLAGE ,max_length=200,default='avant_naissance')
   
   
   
    @classmethod
    def virif_num(cli,num,user):
        for acc in cli.objects.filter(user=user):
                    if num == int((acc.num)[1:]):
                        return True
        return False                
    @classmethod    
    def num_vide (cli,user):
        for i in range(1,len(cli.objects.filter(user=user))+1):
                if not cli.virif_num(i,user):
                    return 'A'+str(i)
        max=0
        for acc in cli.objects.filter(user=user):
            if int(acc.num[1:])>max:
                max=int(acc.num[1:])
        return 'A'+str(max+1)        
    
    def __str__(self):
        return str(self.num)
    # virifier si un accouplement a déja utilisé ou non return bool 
    def __bool__(self):
          return self.state == 'avant_naissance'


class VaccinMalle(Vaccin):
    malle=models.ForeignKey(Malle,on_delete=models.CASCADE ,null=True , blank=True)

class VaccinFemalle(Vaccin):
    femalle=models.ForeignKey(Femalle,on_delete=models.CASCADE ,null=True , blank=True)

class PoidMalle(Poid):
    malle=models.ForeignKey(Malle,on_delete=models.CASCADE ,null=True , blank=True)

class PoidFemalle(Poid):
    femalle=models.ForeignKey(Femalle,on_delete=models.CASCADE ,null=True , blank=True)


class GroupeProduction(models.Model):
        #information principale
        create_at=models.DateField(default=timezone.now)
        cage=models.CharField(max_length=50,null=True,blank=True)
        user=models.ForeignKey(User,on_delete=models.CASCADE,null=True , blank=True)
        acouplement=models.OneToOneField(Accouplement,on_delete=models.CASCADE,null=True , blank=True)
        date_naissance=models.DateField(null=True , blank=True)
        date_souvrage=models.DateField(null=True , blank=True)
        #information de naissance
        nb_lapins_nées=models.IntegerField(default=0)
        nb_lapins_mortes_naissances=models.IntegerField(default=0)
        @classmethod
        # verifier si un cage vide ou non
        def __virif_cage(cls,cage,user):
            for groupe in cls.objects.filter(user=user):
                        if cage == int((groupe.cage)[1:]):
                            return True
            
            return False  
        @classmethod
        # retoiurner un cage vide pour les naveaux groupe    
        def cage_vide (cls,user):
            for i in range(1,len(cls.objects.filter(user=user))+1):
                    if not cls.__virif_cage(i,user):
                        return 'G'+str(i)
            max=0
            for groupe in cls.objects.filter(user=user):
                if int(groupe.cage[1:])>max:
                    max=int(groupe.cage[1:])
            return 'G'+str(max+1)        
        @classmethod    
        # verifier l'existance d'un groupe 
        def virif_groupe(cls,id,user):
            try:
                groupe = GroupeProduction.objects.get(id=id, user=user)
                return True
            except GroupeProduction.DoesNotExist:
                return False
            """ for groupe in cls.objects.filter(user=user):
                if groupe.id == id :
                    return True
            return False  """
        
        # totale des lapins morte dans le groupe
        def totale_mortalité_groupe(self):
           return LapinProduction.objects.filter(groupe=self.id,state='mort').all().count()

        # moyenne des poids des lapins des productions d'un groupe a la naissance  
        def moyenne_poid_groupe_naissance(self):
            moy=0
            nb=0
            for poid in PoidLapinProduction.objects.all():
                if poid.lapin.groupe.id==self.id:
                        if poid.date_mesure==poid.lapin.groupe.date_naissance:
                            nb=nb+1
                            moy=moy+poid.valeur
            if nb!=0:
                return int(moy/nb)
            else:
                return "y'a pas des mesures"    
        # retourner la dernier date de mesure des poids du groupe de production
        def date_dernier_mesure(self):
                    date=""
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe.id==self.id:
                                if date=="":
                                    date=poid.date_mesure
                                elif age(poid.date_mesure)<age(date):
                                    date=poid.date_mesure
                    return date
        # moyenne des poids des lapins des productions du groupe la dernier mesure
        def moyenne_poid_groupe_dernier_mesure(self):
                    moy=0
                    nb=0
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe.id==self.id:
                                if poid.date_mesure==self.date_dernier_mesure():
                                    nb=nb+1
                                    moy=moy+poid.valeur
                    if nb!=0:
                        return int(moy/nb) 
                    else:
                        return "y'a pas des mesures" 
        # les dates de mesure des poids du groupe
        def dates_mesure_poids(self):
            dates=[]
            for poid in PoidLapinProduction.objects.all():
                            if poid.lapin.groupe.id==self.id:
                                    if not(str(poid.date_mesure) in dates):
                                        dates.append(str(poid.date_mesure))
            for i in range(len(dates)-1):
                    min=i
                    for j in range (i+1,len(dates)):
                        if age(dates[j])<age(dates[min]):
                            min=j
                    if age(dates[j])<age(dates[i]):
                            aux=dates[min]
                            dates[min]=dates[i]
                            dates[i]=aux
            return dates
        # moyenne des poids des lapins des productions du groupe a partir de son naissance
        def moyenne_poid_groupe_list(self):
                    dates=self.dates_mesure_poids()
                    moyenne_poids=[]
                    for date in dates:
                        nb=0
                        totale=0
                        for poid in PoidLapinProduction.objects.all():
                            if poid.lapin.groupe.id==self.id:
                                    if str(poid.date_mesure)==date:
                                        nb=nb+1
                                        totale=totale+poid.valeur
                        
                        moyenne_poids.insert(
                            0,
                            {
                                "date":age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date),
                                "mesure":totale/nb,
                            })

                    return moyenne_poids   
        
        #nombre des malles ou des femalles dans le groupe 
        def nombre_malle_groupe(self):
                    nb=0
                    for lapin in LapinProduction.objects.filter(groupe=self):
                        if lapin.sex=="malle":
                                nb=nb+1
                    return nb             
        def nombre_femalle_groupe(self):
                    nb=0
                    for lapin in LapinProduction.objects.filter(groupe=self):
                        if lapin.sex=="femalle":
                                nb=nb+1
                    return nb   
        
        
        # calculer le taux des consomation du groupe entre deux date
        def cons_totale(self,initial_date,final_date):
            totale=0
            for date in list_dates(str(initial_date),str(final_date)):# pd.date_range(end=final_date,start=initial_date).tolist() :
                nb_lapin=GroupeProduction.objects.get(id=self.id).nb_lapins_nées
                # pour eleminer les lapins mortes avant ce date
                for lapin in LapinProduction.objects.filter(groupe=self.id):
                    if lapin.state=='mort':
                        if age(lapin.date_mort)>=age(date):
                            nb_lapin-=1
                if age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date)<25:
                    totale+=(0*nb_lapin)
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))<30:
                    totale+=(5*nb_lapin)
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))<44:
                    totale+=(50*nb_lapin)
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))< 59:
                    totale+=(100*nb_lapin)
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))> 60:
                    totale+=(150*nb_lapin)
            return totale                    
        # retourner une liste de consomation avec sa date
        def cons_totale_list(self,initial_date,final_date):
            totale=[]
            for date in list_dates(str(initial_date),str(final_date)):# pd.date_range(end=final_date,start=initial_date).tolist() :
                nb_lapin=GroupeProduction.objects.get(id=self.id).nb_lapins_nées
                # pour eleminer les lapins mortes avant ce date
                for lapin in LapinProduction.objects.filter(groupe=self.id):
                    if lapin.state=='mort':
                        if age(lapin.date_mort)>=age(date):
                            nb_lapin-=1
                if age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date)<25:
                    totale.append({'cons':0*nb_lapin,'date':str(date)})
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))< 30:
                    totale.append({'cons':5*nb_lapin,'date':str(date)})
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))< 44:
                    totale.append({'cons':50*nb_lapin,'date':str(date)})
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))< 59:
                    totale.append({'cons':100*nb_lapin,'date':str(date)})   
                elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(date))> 60:
                    totale.append({'cons':150*nb_lapin,'date':str(date)})
            return totale 
        # calculer le coup de consomation
        def coup_cons(self,initial_date,final_date,user):
            totale_coup_cons=0
            for cons in self.cons_totale_list(initial_date,final_date):# pd.date_range(end=final_date,start=initial_date).tolist() :
                #if PrixAliments.le_plus_proche_date_a_gauche(cons['date'],user)!={} :
                    nb_lapin=GroupeProduction.objects.get(id=self.id).nb_lapins_nées
                    # pour eleminer les lapins mortes avant ce date
                    for lapin in LapinProduction.objects.filter(groupe=self.id):
                        if lapin.state=='mort':
                            if age(lapin.date_mort)>=age(cons['date']):
                                nb_lapin-=1
                    if  PrixAliments.le_plus_proche_date_a_gauche(cons['date'],user) == {} :
                          return "on peut pas fait le calcule t'as pas encore ajouter le prix des aliments"

                    if(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(cons['date']))< 30:
                        totale_coup_cons+=(5*nb_lapin)*PrixAliments.le_plus_proche_date_a_gauche(cons['date'],user)['prix']
                    elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(cons['date']))< 44:
                        totale_coup_cons+=(50*nb_lapin)*PrixAliments.le_plus_proche_date_a_gauche(cons['date'],user)['prix']
                    elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(cons['date']))< 59:
                        totale_coup_cons+=(100*nb_lapin)*PrixAliments.le_plus_proche_date_a_gauche(cons['date'],user)['prix']
                    elif(age(GroupeProduction.objects.get(id=self.id).date_naissance)-age(cons['date']))> 60:
                        totale_coup_cons+=(150*nb_lapin)*PrixAliments.le_plus_proche_date_a_gauche(cons['date'],user)['prix']
                
            
            return  totale_coup_cons /1000

        # calculer le moyenne des poid des lapins du groupe au sevrage
        def moyenne_poid_souvrage(self):
            moy=0
            nb=0
            for poid in PoidLapinProduction.objects.all():
                if poid.lapin.groupe.id==self.id:
                        if poid.date_mesure==self.date_souvrage :
                            nb=nb+1
                            moy=moy+poid.valeur
            if nb!=0:
                return int(moy/nb) 
            else:
                return "y'a pas des mesures"
        
        ###################////////// les statistiques des vent //////////////////###########
        # return le nombre des lapins vendues  pandant ce mois
        def totale_vent(self):
                    nb=0
                    for lapin in LapinProduction.objects.all():
                        if lapin.groupe == self  and lapin.state=='vendue':
                            if str(lapin.date_vent).find('-')!=(-1):
                                    nb=nb+1
                    return nb   
        # return le nombre des lapins malles vendues  pandant ce mois
        def totale_vent_malle(self):
                    nb=0
                    for lapin in LapinProduction.objects.all():
                        if lapin.groupe == self  and lapin.state=='vendue':
                            if lapin.sex=="malle":
                                if str(lapin.date_vent).find('-')!=(-1):
                                        nb=nb+1
                    return nb   
        # return le nombre des lapins femalles vendues  pandant ce mois
        def totale_vent_femalle(self):
                    nb=0
                    for lapin in LapinProduction.objects.all():
                        if lapin.groupe == self  and lapin.state=='vendue':
                            if lapin.sex=="femalle":
                                if str(lapin.date_vent).find('-')!=(-1):
                                        nb=nb+1
                    return nb   
        # return le plus grands prix dans les prix des lapins vendues  pandant ce mois
        def grand_prix(self):
                    max=0
                    for lapin in LapinProduction.objects.all():
                        if lapin.groupe == self  and lapin.state=='vendue':
                                if str(lapin.date_vent).find('-')!=(-1):
                                        if lapin.prix > max:
                                            max=lapin.prix
                    return max
        #return le plus bas prix dans les prix des lapins vendues  pandant ce mois
        def bas_prix(self):
                    min=10000000000
                    for lapin in LapinProduction.objects.all():
                        if lapin.groupe == self  and lapin.state=='vendue':
                                if str(lapin.date_vent).find('-')!=(-1):  
                                        if lapin.prix < min:
                                            min=lapin.prix
                    if min==10000000000:
                        return 0                        
                    return min            
        ##return le totale des prix dans les prix des lapins vendues  pandant ce mois
        def totale_prix(self):
                    totale=0
                    for lapin in LapinProduction.objects.all():
                        if lapin.groupe == self  and lapin.state=='vendue':
                                if str(lapin.date_vent).find('-')!=(-1):
                                        totale=totale+lapin.prix
                    return totale 
        ##return le moyenne des prix prix dans les prix des lapins vendues  pandant ce mois
        def moy_prix(self):
            if self.TV() !=0 :
                return self.totaleprix(self)/self.TV() 
            return 0                        
      
        # le plus grand poid des poids du dernière groupe du production a la naissance
        def TOPPN(self):
                    max=0
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe==self :
                            if poid.date_mesure==poid.lapin.groupe.date_naissance:
                                if poid.valeur > max:
                                    max=poid.valeur
                    return max  
        ## le plus bas poid des poids du dernière groupe du production a la naissance
        def BASPN(self):
                    min=''
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe==self :
                            if poid.date_mesure==poid.lapin.groupe.date_naissance:
                                if  min == '' or poid.valeur < min:
                                    min=poid.valeur
                    if min=="":
                          return 0
                    return min      
        # le plus grand poid des poids du dernière groupe du production la dernière mesure
        def TOPPDM(self):
                    max=0
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe==self :
                            if poid.date_mesure==poid.lapin.groupe.self.date_dernier_mesure(poid.lapin.groupe):
                                if poid.valeur > max:
                                    max=poid.valeur
                    return max  
        ## le plus bas poid des poids du dernière groupe du production la dernière mesure
        def BASPDM(self):
                    min=""
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe==self :
                            if poid.date_mesure==poid.lapin.groupe.self.date_dernier_mesure(poid.lapin.groupe):
                                if min=='' or poid.valeur < min:
                                    min=poid.valeur
                    if min=='' :return 0
                    return min      
        # le plus grand poid des poids du dernière groupe du production au sevrage
        def TOPPS(self):
                    max=0
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe==self :
                            if poid.date_mesure==poid.lapin.groupe.date_souvrage:
                                if poid.valeur > max:
                                    max=poid.valeur
                    return max         
        ## le plus bas poid des poids du dernière groupe du production au sevrage
        def BASPS(self):
                    min=''
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.groupe==self :
                            if poid.date_mesure==poid.lapin.groupe.date_souvrage:
                                if min == '' or poid.valeur < min:
                                    min=poid.valeur
                    if min == '' :return 0
                    return min      
        
        
        def __str__(self):
            return str(self.cage)     

class LapinProduction(Lapin):
    groupe=models.ForeignKey(GroupeProduction,on_delete=models.CASCADE,default=1)
    sex=models.CharField(max_length=50, default='non verifier',choices=[("femalle","femalle"),("malle","malle"),('non verifier','non verifier')])  
    def delete_(self):
        self.delete()
        groupe=self.groupe
        groupe.nb_lapins_nées-=1
        groupe.save()
    #le poid  du lapin  a la naissance
    def poid_naissance(self):
            for poid in PoidLapinProduction.objects.all():
                if poid.lapin.id==self.id:
                        if poid.date_mesure==poid.lapin.groupe.date_naissance:
                            return poid.valeur
            
            return "y'a pas des mesures"  
    # retourner la dernier date de mesure des poids du lapin
    def date_dernier_mesure(self):
                    date=""
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.id==self.id:
                                if date=="":
                                    date=poid.date_mesure
                                elif age(poid.date_mesure)<age(date):
                                    date=poid.date_mesure
                    return date
        
    #  poids du lapin du productions  la dernier mesure
    def poid_dernier_mesure(self):
                    for poid in PoidLapinProduction.objects.all():
                        if poid.lapin.id==self.id:
                                if poid.date_mesure==self.date_dernier_mesure():
                                    return poid.valeur
                    return "y'a pas des mesures" 
    # poid du lapin au sevrage
    def poid_sevrage(self):
        if self.groupe.date_souvrage!=None:  
            for poid in PoidLapinProduction.objects.all():      
                if poid.date_mesure==self.groupe.date_souvrage:
                    return poid.valeur
        return "y'a pas des mesure"            
    # les dates de mesure des poids du groupe
    def dates_mesure_poids(self):
            dates=[]
            for poid in PoidLapinProduction.objects.all():
                            if poid.lapin.id==self.id:
                                    if not(str(poid.date_mesure) in dates):
                                        dates.append(str(poid.date_mesure))
            # tri selection pour ordonné les date du age plus garnd au age plus petite
            for i in range(len(dates)-1):
                    min=i
                    for j in range (i+1,len(dates)):
                        if age(dates[j])<age(dates[min]):
                            min=j
                    if age(dates[j])<age(dates[i]):
                            aux=dates[min]
                            dates[min]=dates[i]
                            dates[i]=aux
            return dates
    # moyenne des poids des lapins des productions du groupe a partir de son naissance
    def poid_lapin_list(self):
                    
                    
                    dates=self.dates_mesure_poids()
                    poids=[]
                    for date in dates:
                        for poid in PoidLapinProduction.objects.filter(lapin=self.id):
                                    if str(poid.date_mesure)==date:
                                        poids.insert(
                            0,
                            {
                                "date":age(self.groupe.date_naissance)-age(date),
                                "mesure":poid.valeur,
                            })
                        
                        
                    return poids    
    







    def vaccins (self):
        vaccins = [ {
                                    "nom":str(vaccin.nom),
                                    "date_vaccin":str(age_handler(vaccin.date_vaccin)),
                                    "prix":str(vaccin.prix),
                                    "maladie":str(vaccin.maladie),
                    } 

                for vaccin in VaccinLapin.objects.filter(lapin=self.id)
                ]
       
        return vaccins           
    
class PoidLapinProduction(Poid):
    lapin=models.ForeignKey(LapinProduction,on_delete=models.CASCADE ,null=True , blank=True)
    
class VaccinLapin(Vaccin):
    lapin=models.ForeignKey(LapinProduction,on_delete=models.CASCADE ,null=True , blank=True)

# la creation des nauveaux lapins a la creation d'un groupe
def create_lapin(sender,instance,created,**kwargs):
        if created:
                for i in range(int(instance.nb_lapins_mortes_naissances)):
                                LapinProduction.objects.create(
                                                        user=instance.user,
                                                        groupe=instance,                 
                                                        state='mort',
                                                        date_mort=instance.date_naissance,
                                                        
                                                        )              
                                                                                                                                                                
                for i in range(int(instance.nb_lapins_nées)-int(instance.nb_lapins_mortes_naissances)):
                                LapinProduction.objects.create(  
                                                        user=instance.user               ,     
                                                        groupe=instance,
                                                        cage='R'+str(i+1),
                                                        state='production',
                                                        )                  
post_save.connect(create_lapin,sender=GroupeProduction)