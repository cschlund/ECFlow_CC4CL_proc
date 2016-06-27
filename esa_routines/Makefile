#
# Makefile for postprocessing
#

F90=ftn

libfile=lib.ecmwf.cray
include $(libfile)

cfgfile=config_paths.file
include $(cfgfile)

lcommon=-lorac_common
lpre=-lpreproc
lmain=-lorac
lpost=-lpostproc

#performance
FFLAGS= -O noomp -O3 -Oipa3 -Ovector3 -Ofp3 -Ocache3 -Oaggress -Oscalar3 -Othread0 -hmpi1 -hflex_mp=tolerant -rom -ef -em
LFLAGS= -O noomp -O3 -Oipa3 -Ovector3 -Ofp3 -Ocache3 -Oaggress -Oscalar3 -Othread0 -hmpi1 -hflex_mp=tolerant -rom -ef -em
# FFLAGS= -O omp -O3 -Oipa3 -Ovector3 -Ofp3 -Ocache3 -Oaggress -Oscalar3 -Othread3 -hmpi1 -hflex_mp=tolerant -rom -ef -em
# LFLAGS= -O omp -O3 -Oipa3 -Ovector3 -Ofp3 -Ocache3 -Oaggress -Oscalar3 -Othread3 -hmpi1 -hflex_mp=tolerant -rom -ef -em
DFLAGS= -DWRAPPER -DDEBUG

#debugging
# FFLAGS=-O noomp -eD -eC -eI -hfp_trap -ro -K trap=fp -g -ef -em
# LFLAGS=-O noomp -eD -eC -eI -hfp_trap -ro -K trap=fp -g -ef -em
# DFLAGS= -DWRAPPER -DDEBUG

#FFLAGS=-O noomp -eD -eC -eI -hfp_trap -rom -K trap=fp -Gfast -ef -em -DWRAPPER
#LFLAGS=-O noomp -eD -eC -eI -hfp_trap -rom -K trap=fp -Gfast -ef -em -DWRAPPER

OBJ=mpi_wrapper.o clean_up.o prepare_daily.o build_inventory.o

mpi_wrapper: $(OBJ)
	     $(F90) $(LFLAGS) $(DFLAGS) -o mpi_wrapper.x $(OBJ) -L$(LIB_pre) $(lpre) -L$(LIB_main) $(lmain) -L$(LIB_post) $(lpost) $(LIBS) -L$(LIB_common) $(lcommon)
 
%.o:	%.F90
	$(F90) -c $(FFLAGS) $(DFLAGS) $(INC)  $<

 
%.o:	%.F
	$(F90) -c $(FFLAGS) $(INC)  $<

tidy: 
	rm -f *.o 
	rm -f *.mod
	rm -f *.i

clean: 
	rm -f *.o 
	rm -f *.mod
	rm -f *.i
  
