program mpi_wrapper

  !todo:
  !read in more command line arguments: chunksize,mode of operation (static etc) DONE
  !ueberhole find fuer pfade damit es keinen mess-up gibt, checke gemeinsame
  ! strings und fange ab DONE
  !lenke output aus script in loffile um TO BE DONE
  !output oaus wrapper code in monthly logfile DONE
  !1024 bzw. 2048 als variable POSTPONED
  !ziehe aenderungen auf static nach POSTPONED
  !loesche files von erfolgreichem schritt weg wenn naechster schritt
  ! erfolgreich. wie macht man das am besten? DONE
  !schreibe logfile fuer jede cpu bzw. jeden chunk TO BE DONE
  !chunking dynamisch setzen je nachdem wieviele tasks und files und je nach
  ! instrument PARTLY DONE
  !gibt es memory leaks in den teilprogrammen? TO BE INVESTIGATED: NO EVIDENCE
  !starte code mit vorhandenem inventory TO BE DONE
  !Parallelisiere laufen der scripts DONE
  !Andere Abarbeitung des Inventory-Teils DONE
  !Mehr logging TO BE DONE
  !seltsamer output weg machen DONE
  !kommentare TO BE DONE
  !smooth exit by eigentlicher rechenschelife einbauen DONE needs testing
  !move final results to filename as before in script TO BW DONE F
  !only write neccessary fields;O1

  Use mpi

  implicit none

  integer :: ierror,rc, ntasks,mytask,chunk,ifree,icycle,itask,aitask&
       &,bitcounter,stime,i,j,iexit,icpu

  integer :: nfiles_pre,nfiles_liq,nfiles_ice,nfiles_post,nfiles,ifile&
       &,nelements,lower_bound,upper_bound,tag0,tag1,tag2,tag3,tag4,&
       & status(mpi_status_size)

  real(kind=4) :: rchunk,rnumber

  integer, allocatable, dimension(:) :: free,ccounter

  integer, parameter :: shortest_string=256
  integer, parameter :: short_string=1024
  integer, parameter :: long_string=2048

  integer :: rc_pre,rc_liq,rc_ice,rc_post

  integer :: nfiles_conf
  character(len=1024), allocatable, dimension(:) :: file_inventory_conf
  character*1024 :: filepath_conf

  character(len=1024), allocatable, dimension(:) :: file_inventory_pre
  character*1024 :: filepath1024

  character(len=2048), allocatable, dimension(:) ::  file_inventory_liq&
       &,file_inventory_ice,file_inventory_post
  character*2048 :: filepath2048

  character(len=10) :: cmytask

  logical :: lstatic,lidle

  integer :: nx,ny

  integer :: nargs,cpu_counter,valmax,maxcpuval

  character(len=256) :: inventory_file_pre,inventory_file_liq&
       &,inventory_file_ice,inventory_file_post
  character(len=256) :: inventory_file_config,config_paths,config_attributes
  character(len=256) :: single_day_ksh
  character(len=1024) :: dummyfile1024
  character(len=2048) :: dummyfile2048

  character(len=15) :: instrument,wrapper_mode,platform
  character(len=4) :: year
  character(len=2) :: month
  character(len=512) :: jid,log_dir,out_dir,L2_file_list_dir
  character(len=1024) :: logfile,ilogfile,L2_file_list,L2_sum_file_list
  !character(len=256) :: to_upper


  ! Openmp variables
  integer                                :: nompthreads
  integer                                           :: omp_get_max_threads
  integer                                           :: omp_get_num_threads

  INTERFACE

     Pure Function to_upper (str) Result (string)

       !   ==============================
       !   Changes a string to upper case
       !   ==============================

       Implicit None

       Character(*), Intent(In) :: str
       Character(LEN(str))      :: string

       Integer :: ic, i

       Character(26), Parameter :: cap = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
       Character(26), Parameter :: low = 'abcdefghijklmnopqrstuvwxyz'

     End Function to_upper

  END INTERFACE


  !Initialize MPI
  call MPI_INIT(ierror)
  call MPI_COMM_SIZE(MPI_COMM_WORLD,ntasks,ierror)
  call MPI_COMM_RANK(MPI_COMM_WORLD,mytask,ierror)


  !use master to read in command-line arguments from starting script
  if(mytask .eq. 0 ) then

     cpu_counter=0

     ! get number of arguments
     nargs = COMMAND_ARGUMENT_COUNT()
     ! if more than one argument passed, all inputs on command line
     if(nargs .eq. 13) then

        CALL GET_COMMAND_ARGUMENT(1,inventory_file_config)
        CALL GET_COMMAND_ARGUMENT(2,instrument)
        CALL GET_COMMAND_ARGUMENT(3,platform)
        CALL GET_COMMAND_ARGUMENT(4,month)
        CALL GET_COMMAND_ARGUMENT(5,year)
        CALL GET_COMMAND_ARGUMENT(6,wrapper_mode)
        CALL GET_COMMAND_ARGUMENT(7,jid)
        CALL GET_COMMAND_ARGUMENT(8,log_dir)
        CALL GET_COMMAND_ARGUMENT(9,out_dir)
        CALL GET_COMMAND_ARGUMENT(10,L2_file_list_dir)
        CALL GET_COMMAND_ARGUMENT(11,config_paths)
        CALL GET_COMMAND_ARGUMENT(12,config_attributes)
        CALL GET_COMMAND_ARGUMENT(13,single_day_ksh)

     endif

     config_paths=trim(adjustl(config_paths))
     !write(*,*) 'cp',trim(adjustl(config_paths))
     config_attributes=trim(adjustl(config_attributes))
     !write(*,*) 'ca', trim(adjustl(config_attributes))
     single_day_ksh=trim(adjustl(single_day_ksh))
     write(*,*) 'single_day_ksh in mpi_wrapper.F90: ', trim(adjustl(single_day_ksh))



     !open file for stdout   
     logfile=trim(adjustl(trim(adjustl(log_dir))//'/'//'proc_2_logfile_'&
          &//trim(adjustl(jid))//'.log'))

     open(11,file=trim(adjustl(logfile)),status='replace')

     !open file for L2 output list
     L2_file_list=trim(adjustl(trim(adjustl(L2_file_list_dir))//'/'//'L2_ncfile_list_l2b_' &
          & // trim(instrument) // '_' // to_upper(trim(platform)) // '_' // &
          & trim(year) // '_' // trim(month) //'.txt'))

     open(12,file=trim(adjustl(L2_file_list)),status='replace')

     L2_sum_file_list=trim(adjustl(trim(adjustl(L2_file_list_dir))//'/'//'L2_ncfile_list_l2b_sum_'&
          & // trim(instrument) // '_' // to_upper(trim(platform)) // '_' // &
          & trim(year) // '_' // trim(month) //'.txt'))

     open(13,file=trim(adjustl(L2_sum_file_list)),status='replace')


     !set threadnumber to default=single-threaded
     nompthreads=1

     ! Check how many threads are available?
#ifdef _OPENMP
     nompthreads=omp_get_max_threads()
#endif

     write(11,*) '#############################################################'
     write(11,*) '#############################################################'
     write(11,*) "STARTING PARALLEL PROCESSING"
     write(11,*)  '-------------------------------------------------------------'
     write(11,*)  '-------------------------------------------------------------'
     write(11,*) 'CHAIN running on: ', nompthreads, 'threads'
     write(11,*) 'NO HYPERTHREADING IF NOT EXPLICITLY TURNED-ON!!!'
     write(11,*) 'Number of tasks assigned:', ntasks
     write(11,*) 'A total of ', nompthreads*ntasks,' CPUs is in use'

     !set mode of operation (maintain only dynamic)
     lstatic=.false.
     if(trim(adjustl(wrapper_mode)) .eq. 'stat') lstatic=.true.
     if(trim(adjustl(wrapper_mode)) .eq. 'dyn') lstatic=.false.
     write(11,*)  'WRAPPER IN MODE ', trim(adjustl(wrapper_mode))
     lidle=.false.

     open(25,file=trim(adjustl(inventory_file_config)),status='old')
     read(25,*) nfiles_conf


  endif

  !bcast instrument and platform etc.
  call mpi_bcast(jid,512,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_bcast(log_dir,512,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_bcast(instrument,15,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_bcast(platform,15,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_bcast(year,4,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_bcast(month,2,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)

  !bcast paths to cpus
  call mpi_bcast(config_paths,256,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_bcast(config_attributes,256,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_bcast(single_day_ksh,256,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)

  !master bcasts "nfiles_conf" to all cpus
  call mpi_bcast(nfiles_conf,1,MPI_INT,0,MPI_COMM_WORLD,ierror)
  call mpi_barrier(MPI_COMM_WORLD,ierror)

  !allocate inventory on all cpus
  allocate(file_inventory_conf(nfiles_conf))

  !master reads now the config inventory file
  if(mytask .eq. 0 ) then

     do ifile=1,nfiles_conf

        read(25,100) filepath1024
        file_inventory_conf(ifile)=trim(adjustl(filepath1024))
        write(11,*) 'master',mytask,ifile,nfiles_conf&
             &,trim(adjustl(file_inventory_conf(ifile)))

     enddo

     close(25)

     !#ifdef
     call flush(11)

  endif

  !bcast config files to cpus
  call mpi_bcast(file_inventory_conf,nfiles_conf*1024,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
  call mpi_barrier(MPI_COMM_WORLD,ierror)
  !set chunk to 1(assume we always have ncpus>>ndays)
  chunk=1

  !set icycle: counts iterations of outer loop
  icycle=0
  allocate(free(0:ntasks-1))
  allocate(ccounter(0:ntasks-1))

  free=1
  ccounter=0
  upper_bound=-1
  itask=0

  !this is crucial as it determines the increment of work
  bitcounter=0
  !set exit flag for endless loop
  iexit=0

  !master cpu only controls others, does nothing else, too bad
  do

     !if i am worker and i am free, tell master
     if( mytask .ne. 0 .and. free(mytask) .eq. 1)  then
        tag3=3
        ifree=1
        call mpi_send(ifree,1,mpi_integer,0,tag3,mpi_comm_world,ierror)
        !write(*,*) 'free signal sent',mytask,iexit
     endif

     !master monitors workers
     if(mytask .eq. 0) then

        !if there is still work to do, wait for workers to report all is done
        tag3=3
        call mpi_recv(ifree,1,mpi_integer,mpi_any_source,tag3,mpi_comm_world,status,ierror)
        itask=status(mpi_source)
        write(11,*) 'config work done from cpu',itask

        free(itask)=1

        !if all files are processed, send to all workers the abort signal
        if(upper_bound .eq. nfiles_conf) then
           if(sum(free(0:ntasks-1)) .eq. ntasks ) then
              write(11,*) 'config work distribution was',ccounter,'sum'&
                   &,sum(ccounter)*chunk,'nfiles',nfiles_conf,ntasks,icycle
              !sent exit signal to worker
              tag0=0
              iexit=1
              do icpu=1,ntasks-1
                 aitask=icpu
                 call mpi_send(iexit,1,mpi_integer,aitask,tag0,mpi_comm_world,ierror)
                 write(11,*) 'iexit signal sent (close)',mytask,aitask,iexit
              enddo
              exit
           else
              cycle
           endif
        else
           !if worker is free give it work
           if(ifree .eq. 1 ) then
              free(itask)=0

              !determine new work load based on previously done work
              lower_bound=(chunk*bitcounter)+1
              upper_bound=min((bitcounter+1)*chunk,nfiles_conf)
              aitask=itask

              !sent continue signal to worker
              tag0=0
              iexit=0
              call mpi_send(iexit,1,mpi_integer,aitask,tag0,mpi_comm_world,ierror)
              write(11,*) 'iexit signal sent (free)',mytask,aitask,iexit

              !sent work assigment to worker
              tag1=1
              call mpi_send(lower_bound,1,mpi_integer,aitask,tag1,mpi_comm_world,ierror)

              tag2=2
              call mpi_send(upper_bound,1,mpi_integer,aitask,tag2,mpi_comm_world,ierror)

              !P write(*,*) 'work assigned to cpu',aitask,lower_bound,upper_bound
              ccounter(aitask)=ccounter(aitask)+1
              write(11,*) 'config work assigned to cpu',aitask,lower_bound,upper_bound
              !write(*,*) 'free', free


              icycle=icycle+1

              bitcounter=bitcounter+1

           endif

        endif

     endif

     !if i am worker
     if( mytask .ne. 0) then

        !receive signal from master
        tag0=0
        call mpi_recv(iexit,1,mpi_integer,0,tag0,mpi_comm_world,status,ierror)
        !write(*,*) 'iexit signal received',mytask,iexit

        !if signal "go"
        if(iexit .eq. 0 ) then

           !receive work load from master
           tag1=1
           call mpi_recv(lower_bound,1,mpi_integer,0,tag1,mpi_comm_world,status,ierror)
           free(mytask)=0
           tag2=2
           call mpi_recv(upper_bound,1,mpi_integer,0,tag2,mpi_comm_world,status,ierror)

           !write(*,*) 'slave',mytask,nfiles!,trim(adjustl(file_inventory_pre))

           !do some work 
           do ifile=lower_bound,upper_bound

              filepath1024=trim(adjustl(file_inventory_conf(ifile)))
              call prepare_daily(filepath1024,single_day_ksh,config_paths,config_attributes,mytask)

           enddo

           !report work is done, sent at next call of loop
           free(mytask)=1

           !if signal "stop" jump out of loop
        elseif(iexit .eq. 1 ) then
           exit     
        endif

     endif

  enddo

  deallocate(free)
  deallocate(ccounter)



  !write(*,*) 'task,exit',mytask,iexit
  !wait till all workers are done
  call mpi_barrier(MPI_COMM_WORLD,ierror)

  !master builds inventory files
  if(mytask .eq. 0) then 
     write(11,*) 'building inventory',mytask
     call flush(11)
  endif

  !if(ntasks .lt. 4) then
  if(mytask .eq. 0 ) then
     call build_inventory(log_dir,out_dir,jid,&
          & instrument,platform,month,year,&
          & inventory_file_pre,inventory_file_liq,inventory_file_ice,inventory_file_post,mytask,ntasks)
  endif
  !use first four cpus to build inventories
  !elseif(ntasks .ge. 4) then
!!$     if(mytask .ge. 0 .and. mytask .le. 3) then
!!$        call build_inventory(log_dir,out_dir,jid,&
!!$             & instrument,platform,month,year,&
!!$             & inventory_file_pre,inventory_file_liq,inventory_file_ice,inventory_file_post,mytask,ntasks)
!!$     endif
!!$  endif
  !everybody wait till master is done
  call mpi_barrier(MPI_COMM_WORLD,ierror)


  !master reads inventory in again
  if(mytask .eq. 0 ) then

     open(15,file=trim(adjustl(inventory_file_pre)),status='old')
     open(16,file=trim(adjustl(inventory_file_liq)),status='old')
     open(17,file=trim(adjustl(inventory_file_ice)),status='old')
     open(18,file=trim(adjustl(inventory_file_post)),status='old')

     read(15,*) nfiles_pre
     read(16,*) nfiles_liq
     read(17,*) nfiles_ice
     read(18,*) nfiles_post

     !check file number is correct otherwise abort job
     if(nfiles_pre .eq. nfiles_liq .and. nfiles_liq .eq. nfiles_ice .and. nfiles_ice .eq. nfiles_post) then

        nfiles=nfiles_pre

     else

        write(11,*) 'FAILED: # of files not equal:',nfiles_pre,nfiles_liq,nfiles_ice,nfiles_post
        close(11)
        call mpi_abort(mpi_comm_world,rc,ierror)
        stop

     endif

     !set default chunk sizes
     chunk=1
     !set chunk according to processed instrument
     if(trim(adjustl(instrument)) .eq. 'MODIS' .or. trim(adjustl(instrument)) .eq. 'modis') chunk=1
     if(trim(adjustl(instrument)) .eq. 'AVHRR' .or. trim(adjustl(instrument)) .eq. 'avhrr') chunk=1

     !if more work assignable than existing reduce assignable work
     if((ntasks-1)*chunk .gt. nfiles) then
        chunk=int(nfiles/float(ntasks))
     endif
     !if more CPUs available than files
     if((ntasks-1) .gt. nfiles) then
        !call OMP_SET_NUM_THREADS(num_threads) !could shovel those abundant cpus into threads?
        write(11,*) 'PROCESSING FAILED!!!! TOO MANY CPUS'
        call flush(11)
        close(11)
        call mpi_abort(mpi_comm_world,rc,ierror)
     endif
     chunk=max(chunk,1)
     write(11,*) 'Chunk set statically to: ',chunk

  endif


  !master bcasts "nfiles" to all cpus
  call mpi_bcast(nfiles,1,MPI_INT,0,MPI_COMM_WORLD,ierror)
  call mpi_barrier(MPI_COMM_WORLD,ierror)


  !allocate inventory on all cpus
  allocate(file_inventory_pre(nfiles))
  !file_inventory_pre=''

  allocate(file_inventory_liq(nfiles))
  !file_inventory_liq=''

  allocate(file_inventory_ice(nfiles))
  !file_inventory_ice=''

  allocate(file_inventory_post(nfiles))
  !file_inventory_post=''


  !master reads now the inventory files
  if(mytask .eq. 0 ) then

     do ifile=1,nfiles

        read(15,100) filepath1024
        file_inventory_pre(ifile)=trim(adjustl(filepath1024))
        write(11,*) 'master',mytask,ifile,nfiles,trim(adjustl(file_inventory_pre(ifile)))

        read(16,200) filepath2048
        file_inventory_liq(ifile)=trim(adjustl(filepath2048))

        read(17,200) filepath2048
        file_inventory_ice(ifile)=trim(adjustl(filepath2048))

        read(18,200) filepath2048

        file_inventory_post(ifile)=trim(adjustl(filepath2048))

        ! write path of L2 post-processed file to list
        call create_L2_list_or_file(file_inventory_post(ifile), instrument, &
             platform, year, month, config_attributes, .false.)

     enddo

     close(12)
     close(13)
     close(15)
     close(16)
     close(17)
     close(18)

     nelements=size(file_inventory_pre)
     write(11,*) nelements,'elements to process'   
     call flush(11)

  endif

  !use this if static work distribution on the available cpus is desired not maintained at the moment)
  if(lstatic) then

     !master bcasts "file_inventory" to all cpus
     call mpi_bcast(file_inventory_pre,nfiles*1024,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_bcast(file_inventory_liq,nfiles*2048,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_bcast(file_inventory_ice,nfiles*2048,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_bcast(file_inventory_post,nfiles*2048,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_barrier(MPI_COMM_WORLD,ierror)

100  format(a1024)
200  format(a2048)

     !now compute how many files go to each cpu
     rchunk=nfiles/float(ntasks)

     !that way a couple of cpus remain idle, too bad
     if(lidle) then

        chunk=ceiling(rchunk)
        chunk=min(chunk,1)
        lower_bound=(chunk*mytask)+1
        upper_bound=min((mytask+1)*chunk,nfiles)     

        !that way the last cpu has to go through more files than the others, too bad
     else

        chunk=floor(rchunk)
        chunk=min(chunk,1)
        lower_bound=(chunk*mytask)+1
        upper_bound=min((mytask+1)*chunk,nfiles)
        if(mytask .eq. ntasks)  upper_bound=max((mytask+1)*chunk,nfiles)

     endif

     !now each cpu has its work in terms of a loop chunk assigned
     !start looping now
     !do some work 
!     do ifile=lower_bound,upper_bound

        !        write(11,*) 'RUNNING PREPROC'
        !        write(11,*) chunk,mytask,ifile,trim(adjustl(file_inventory_pre(ifile)))
        !        call preprocessing(mytask,ntasks,lower_bound,upper_bound,adjustl(file_inventory_pre(ifile)))

        !        write(11,*) 'RUNNING PROC',chunk,mytask,ifile,lower_bound,upper_bound,trim(adjustl(file_inventory_liq(ifile)))
        !        dummyfile2048=adjustl(file_inventory_liq(ifile))
        !write(11,*) 'dummyfile',trim(adjustl(dummyfile2048))
        !        call ECP(mytask,ntasks,lower_bound,upper_bound,dummyfile2048)
        !              
        !        call post_process_level2


!     enddo

     !use this if dynamic work assignment is desired
  else

     !chunk has been set above as default, e.g. chunk=10

     !bcast inventories to all cpus (could just sent path to be processed)
     call mpi_bcast(file_inventory_pre,nfiles*1024,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_bcast(file_inventory_liq,nfiles*2048,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_bcast(file_inventory_ice,nfiles*2048,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_bcast(file_inventory_post,nfiles*2048,MPI_CHARACTER,0,MPI_COMM_WORLD,ierror)
     call mpi_barrier(MPI_COMM_WORLD,ierror)

#ifdef DEBUG
     if(mytask .ne. 0 ) then 
        Write( cmytask, '(i10)' ) mytask
        ilogfile=trim(adjustl(trim(adjustl(log_dir))//'/'//'proc_2_logfile_'//trim(adjustl(jid))//&
             & '_CPU_'//trim(adjustl(cmytask))//'.log'))
        open(300+mytask,file=trim(adjustl(ilogfile)),status='replace')
     endif
#endif


     !set icylce: counts how many times outer loop has been run through
     icycle=0
     allocate(free(0:ntasks-1))
     allocate(ccounter(0:ntasks-1))

     free=1
     ccounter=0
     upper_bound=-1
     !lower_bound=1
     !upper_bound=lower_bound+chunk-1
     itask=0
     maxcpuval=1

     !this is crucial as it determines the increment of work
     bitcounter=0

     !set exit flag for endless loop
     iexit=0

     !master cpu only controls others, does nothing else, too bad
     do

        !if i am worker and i am free, tell master
        if( mytask .ne. 0 .and. free(mytask) .eq. 1 )  then
           tag3=3
           ifree=1
           call mpi_send(ifree,1,mpi_integer,0,tag3,mpi_comm_world,ierror)
        endif

        !master monitors workers
        if(mytask .eq. 0 ) then

           !if there is still work to do, wait for workers to report all is done
           tag3=3
           call mpi_recv(ifree,1,mpi_integer,mpi_any_source,tag3,mpi_comm_world,status,ierror)
           itask=status(mpi_source)

           !reset chunk dynamically
           !           valmax=maxval(ccounter(1:ntasks-1))
           !           if(valmax .gt. maxcpuval) then
           !              maxcpuval=valmax
           !              chunk=min(int(0.25*(nfiles-upper_bound)/float((ntasks-1))),chunk)
           !              chunk=max(chunk,1)
           !              write(11,*) 'Chunk set dynamically to: ',chunk
           !           endif

!!$           valmin=minval(ccounter(1:ntasks-1))
!!$           if(valmin .gt. mincpuval) then
!!$              mincpuval=valmin
!!$              chunk=max(int(0.25*(nfiles-upper_bound)/float((ntasks-1))),1)
!!$              chunk=max(chunk,1)
!!$           endif


           free(itask)=1

           !if all files are processed, send to all workers the abort signal
           if(upper_bound .eq. nfiles) then

              cpu_counter=cpu_counter+1
              write(11,*) 'Closing, work done from cpu',itask,cpu_counter/float((ntasks-1))*100.0,cpu_counter,ntasks-1,ntasks-1-cpu_counter
              call flush(11)

              if(sum(free(0:ntasks-1)) .eq. ntasks ) then
                 write(11,*) 'work distribution was',ccounter,'sum',sum(ccounter)*chunk,'nfiles',nfiles,ntasks,icycle

                 !sent exit signal to worker
                 tag0=0
                 iexit=1
                 do icpu=1,ntasks-1
                    aitask=icpu
                    call mpi_send(iexit,1,mpi_integer,aitask,tag0,mpi_comm_world,ierror)
                    write(11,*) 'iexit signal sent (close)',mytask,aitask,iexit            
                    !call mpi_abort(mpi_comm_world,rc,ierror)
                 enddo
                 exit
              else
                 cycle
              endif
           else

              !P           write(*,*) 'work done from cpu',itask,ccounter(itask)
              write(11,*) 'Running, work done from cpu',itask
              call flush(11)

              !if worker is free give it work
              if(ifree .eq. 1 ) then
                 free(itask)=0

                 !determine new work load based on previously done work
                 lower_bound=(chunk*bitcounter)+1
                 upper_bound=min((bitcounter+1)*chunk,nfiles)

                 !MJ TEST lower_bound=upper_bound+1
                 !MJ TEST upper_bound=min(lower_bound+chunk-1,nfiles)


                 aitask=itask

                 !sent continue signal to worker
                 tag0=0
                 iexit=0
                 call mpi_send(iexit,1,mpi_integer,aitask,tag0,mpi_comm_world,ierror)
                 write(11,*) 'iexit signal sent (free)',mytask,aitask,iexit

                 !sent work assigment to worker
                 tag1=1
                 call mpi_send(lower_bound,1,mpi_integer,aitask,tag1,mpi_comm_world,ierror)

                 tag2=2
                 call mpi_send(upper_bound,1,mpi_integer,aitask,tag2,mpi_comm_world,ierror)

                 !P write(*,*) 'work assigned to cpu',aitask,lower_bound,upper_bound
                 ccounter(aitask)=ccounter(aitask)+1
                 write(11,*) 'work assigned to cpu',aitask,lower_bound,upper_bound
                 !write(*,*) 'free', free


                 icycle=icycle+1

                 bitcounter=bitcounter+1

              endif

           endif

        endif

        !if i am worker
        if(mytask .ne. 0) then

           !receive signal from master
           tag0=0
           call mpi_recv(iexit,1,mpi_integer,0,tag0,mpi_comm_world,status,ierror)
           !write(*,*) 'iexit signal received',mytask,iexit

           !if signal "go"           
           if(iexit .eq. 0 ) then

              !receive work load from master
              tag1=1
              call mpi_recv(lower_bound,1,mpi_integer,0,tag1,mpi_comm_world,status,ierror)
              free(mytask)=0
              tag2=2
              call mpi_recv(upper_bound,1,mpi_integer,0,tag2,mpi_comm_world,status,ierror)

#ifdef DEBUG
              write(300+mytask,*) 'Worker ',mytask,'processing: ',lower_bound,upper_bound
#endif

              !do some work 
              do ifile=lower_bound,upper_bound

                 !set some return codes
                 rc_pre=1
                 rc_liq=1
                 rc_ice=1 
                 rc_post=1

                 !run preprocessing
                 dummyfile1024=adjustl(file_inventory_pre(ifile))
#ifdef DEBUG
                 write(300+mytask,*) 'Worker ',mytask,'processing: ',ifile,trim(adjustl(dummyfile1024))
#endif

                 call preprocessing(mytask,ntasks,lower_bound,upper_bound,dummyfile1024,rc_pre)

                 !run main for water
                 dummyfile2048=adjustl(file_inventory_liq(ifile))
                 call ECP(mytask,ntasks,lower_bound,upper_bound,dummyfile2048,rc_liq)

                 !run main for ice
                 dummyfile2048=adjustl(file_inventory_ice(ifile))
                 call ECP(mytask,ntasks,lower_bound,upper_bound,dummyfile2048,rc_ice)

                 !run postprocessing
                 dummyfile1024=adjustl(file_inventory_post(ifile))
                 call post_process_level2(mytask,ntasks,lower_bound,upper_bound,dummyfile1024,rc_post)

                 rc_pre=0
                 rc_liq=0
                 rc_ice=0
                 rc_post=0

                 !cleanup and rename if everything worked well
                 if(rc_pre .eq. 0 .and.&
                      & rc_ice .eq. 0 .and.&
                      & rc_liq .eq. 0 .and.&
                      & rc_post .eq. 0) then
                    dummyfile1024=adjustl(file_inventory_pre(ifile))
                    !call clean_up_pre(dummyfile1024)
                    dummyfile2048=adjustl(file_inventory_liq(ifile))
                    !call clean_up_main(dummyfile2048)
                    dummyfile1024=adjustl(file_inventory_post(ifile))
                    write(*,*) "Calling create_L2_list_or_file"
                    call create_L2_list_or_file(dummyfile1024,instrument, &
                         platform,year,month,config_attributes,.true.)
                 endif

#ifdef DEBUG
                 call flush(300+mytask)
#endif

              enddo
              !report work is done, sent at next call of loop
              free(mytask)=1

              !if signal "stop" jump out of loop
           elseif(iexit .eq. 1 ) then
              exit     
           endif

        endif

     enddo

     deallocate(free)
     deallocate(ccounter)

  endif

  call mpi_barrier(MPI_COMM_WORLD,ierror)  

  !close processing
  if(mytask .eq. 0) then
     write(11,*)
     write(11,*) '##################################################'
     write(11,*) '##################################################'
     write(11,*) 'Closing down processing,exit',mytask,iexit
     write(11,*) '##################################################'
     write(11,*) '##################################################'
     call flush(11)
     close(11)
  elseif(mytask .ne. 0 ) then 
#ifdef DEBUG
     call flush(300+mytask)
     close(300+mytask)
#endif
  endif

  call mpi_barrier(MPI_COMM_WORLD,ierror)

  call MPI_FINALIZE(ierror)

end program mpi_wrapper

!===================================================================

Pure Function to_upper (str) Result (string)

  !   ==============================
  !   Changes a string to upper case
  !   ==============================

  Implicit None

  Character(*), Intent(In) :: str
  Character(LEN(str))      :: string

  Integer :: ic, i

  Character(26), Parameter :: cap = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  Character(26), Parameter :: low = 'abcdefghijklmnopqrstuvwxyz'

  !   Capitalize each letter if it is lowecase
  string = str
  do i = 1, LEN_TRIM(str)
     ic = INDEX(low, str(i:i))
     if (ic > 0) string(i:i) = cap(ic:ic)
  end do

End Function to_upper
