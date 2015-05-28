subroutine clean_up_pre(string)

  implicit none

  character(len=1024) :: string
  character(len=256) :: dir
  character(len=1280) :: directory

  character(len=1536) :: command_line

  integer :: cut_off
  integer :: estat,cstat

  character(len=1024) :: cmsg

  dir='pre_proc'
  
  !get path to preprocessing results from path to driver file
  cut_off=index(trim(adjustl(string)),'/',BACK=.true.)

  directory=trim(adjustl(string(1:cut_off)))//trim(adjustl(dir))

  command_line="rm -rf "//trim(adjustl(directory))

  write(*,*)  "Clean_up_pre command line call = ", trim(adjustl(command_line))

  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)

end subroutine clean_up_pre


subroutine clean_up_main(string)

  implicit none

  character(len=2048) :: string
  character(len=256) :: dir
  character(len=2304) :: directory

  character(len=2560) :: command_line

  integer :: cut_off
  integer :: estat,cstat

  character(len=1024) :: cmsg

  dir='main'
  
  !get path to preprocessing results from path to driver file
  cut_off=index(trim(adjustl(string)),'/',BACK=.true.)

  directory=trim(adjustl(string(1:cut_off)))//trim(adjustl(dir))

  command_line="rm -rf "//trim(adjustl(directory))

  write(*,*)  "Clean_up_main command line call = ", trim(adjustl(command_line))

  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)

end subroutine clean_up_main

 
 
subroutine create_L2_list_or_file(string,instrument,platform,year,month,move_L2)

  character(len=1024) :: string
  character(len=15)   :: instrument,platform
  character(len=1024) :: finalprimary, finalsecondary, sourceprimary
  character(len=4)    :: year
  character(len=5)    :: month,day,hour,min
  character(len=16)   :: prefix_dummy
  character(len=4)    :: suffix_dummy
  character(len=11)   :: suffix_source
  character(len=3)    :: suffix_target
  integer             :: cut_off,cut_off_head,cut_off_tail
  character(len=256)  :: dri_file
  character(len=6)    :: yyyymm
  character(len=2560) :: command_line
  character(len=2304) :: directory
  character(len=256)  :: dir
  integer             :: estat,cstat,i,ic
  character(len=1024) :: cmsg
  character(len=256)  :: to_upper
  logical             :: move_L2 ! rename L2 output file?

  dir='post'
  prefix_dummy='postproc_driver_'
  suffix_dummy='.dat'
  suffix_source='.primary.nc'
  suffix_target='.nc'

  write(*,*) "in move_post"

  if(trim(adjustl(instrument)) .eq. 'AVHRR' .or. trim(adjustl(instrument)) .eq. 'avhrr') then

     cut_off = index(trim(adjustl(string)),'/',BACK=.true.)
     directory = trim(adjustl(string(1:cut_off)))
     write(*,*) cut_off,trim(directory)

     cut_off=index(trim(adjustl(string)),'/',BACK=.true.)
     dri_file=trim(adjustl(string(cut_off+1:len_trim(string))))
     write(*,*) cut_off,trim(adjustl(dri_file))

     yyyymm=trim(adjustl(year))//trim(adjustl(month))
     write(*,*) yyyymm

     cut_off_head=verify(trim(adjustl(dri_file)),prefix_dummy)
     write(*,*) cut_off_head
     cut_off_tail=index(trim(adjustl(dri_file)),suffix_dummy)
     write(*,*) cut_off_tail
     sourceprimary = trim(adjustl(dri_file(cut_off_head:cut_off_tail-1))) // suffix_source
     write(*,*) trim(sourceprimary)

     cut_off=index(trim(adjustl(dri_file)),yyyymm)
     write(*,*) 'co',cut_off

     day=trim(adjustl(dri_file(cut_off+6:cut_off+7)))
     write(*,*) 'day',day

     hour=trim(adjustl(dri_file(cut_off+9:cut_off+10)))
     write(*,*) 'hour',hour

     min=trim(adjustl(dri_file(cut_off+11:cut_off+12)))
     write(*,*) 'min',min

     platform = to_upper(platform)

     ! TO DO: import file version
     finalprimary = trim(yyyymm) // trim(day) // trim(hour) // trim(min) // '00-ESACCI-L2_CLOUD-CLD_PRODUCTS-' // trim(instrument) // 'GAC-' // trim(platform) // '-fv1.0' // trim(suffix_target)

     if (move_L2) then

        command_line = "mv -f " // trim(directory) // trim(dir) // "/" // trim(sourceprimary) // " " // trim(directory) // trim(dir) // "/" // trim(finalprimary)
        call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)

        write(*,*)  "L2 output file path = ", trim(directory) // trim(dir) // "/" // trim(finalprimary)

     else

        write(12,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"
        write(13,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"

     endif

  endif

  if (trim(adjustl(instrument)) .eq. 'MODIS' .or. trim(adjustl(instrument)) .eq. 'modis') then

     cut_off = index(trim(adjustl(string)),'/',BACK=.true.)
     directory = trim(adjustl(string(1:cut_off)))
     write(*,*) cut_off,trim(directory)

     cut_off=index(trim(adjustl(string)),'/',BACK=.true.)
     dri_file=trim(adjustl(string(cut_off+1:len_trim(string))))
     write(*,*) cut_off,trim(adjustl(dri_file))

     yyyymm=trim(adjustl(year))//trim(adjustl(month))
     write(*,*) yyyymm

     cut_off_head=verify(trim(adjustl(dri_file)),prefix_dummy)
     write(*,*) cut_off_head
     cut_off_tail=index(trim(adjustl(dri_file)),suffix_dummy)
     write(*,*) cut_off_tail
     sourceprimary = trim(adjustl(dri_file(cut_off_head:cut_off_tail-1))) // suffix_source
     write(*,*) trim(sourceprimary)

     cut_off=index(trim(adjustl(dri_file)),yyyymm)
     write(*,*) 'co',cut_off

     day=trim(adjustl(dri_file(cut_off+6:cut_off+7)))
     write(*,*) 'day',day

     hour=trim(adjustl(dri_file(cut_off+9:cut_off+10)))
     write(*,*) 'hour',hour

     min=trim(adjustl(dri_file(cut_off+11:cut_off+12)))
     write(*,*) 'min',min

     finalprimary = trim(yyyymm) // trim(day) // trim(hour) // trim(min) // & 
          '00-ESACCI-L2_CLOUD-CLD_PRODUCTS-' // trim(instrument) // 'GAC-' // & 
          trim(platform) // '-fv1.0' // trim(suffix_target)

     if (move_L2) then

        command_line = "mv -f " // trim(directory) // trim(dir) // "/" // trim(sourceprimary) // " " // trim(directory) // trim(dir) // "/" // trim(finalprimary)
        call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)

        write(*,*)  "L2 output file path = ", trim(directory) // trim(dir) // "/" // trim(finalprimary)

     else

        write(12,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"
        write(13,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"

     endif

  endif

end subroutine create_L2_list_or_file

