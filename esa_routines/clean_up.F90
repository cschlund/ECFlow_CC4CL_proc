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

subroutine create_L2_list_or_file(string,instrument,platform,year,month,config_attributes,move_L2, finalPrimaryFullPath)

  character(len=1024) :: string
  character(len=15)   :: instrument,platform, file_version
  character(len=1024) :: finalprimary, finalsecondary, sourceprimary, sourcesecondary
  character(len=1024),intent(out) :: finalPrimaryFullPath
  character(len=4)    :: year
  character(len=5)    :: month,day,hour,min
  character(len=16)   :: prefix_dummy
  character(len=4)    :: suffix_dummy
  character(len=15)   :: suffix_source, suffix_source_secondary
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
  character(len=256)  :: config_attributes

  dir='post'
  prefix_dummy='postproc_driver_'
  suffix_dummy='.dat'
  suffix_source='.primary.nc'
  suffix_source_secondary='.secondary.nc'
  suffix_target='.nc'

  write(*,*) "in create_L2_list_or_file"

  write(*,*) "call get_file_version"
  call get_file_version(config_attributes, file_version)
  write (*,*) 'in create_L2_list_or_file:  file_version is = ', trim(file_version)

  if(trim(adjustl(instrument)) .eq. 'AVHRR' .or. trim(adjustl(instrument)) .eq. 'avhrr') then
     ! 19880118070900-ESACCI-L2_CLOUD-CLD_PRODUCTS-AVHRRGAC-NOAA10-fv2.0.nc
     ! ECC_GAC_avhrr_noaa10_99999_19880118T0709402Z_19880118T0900197Z.secondary.nc
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
     sourceprimary = trim(adjustl(dri_file(cut_off_head:cut_off_tail-1))) // trim(adjustl(suffix_source))
     sourcesecondary = trim(adjustl(dri_file(cut_off_head:cut_off_tail-1))) // trim(adjustl(suffix_source_secondary))
     write(*,*) "sourceprimary in wrapper = ", trim(sourceprimary)
     write(*,*) "sourcesecondary in wrapper = ", trim(sourcesecondary)

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
     finalprimary = trim(yyyymm) // trim(day) // trim(hour) // trim(min) // '00-ESACCI-L2_CLOUD-CLD_PRODUCTS-' // trim(instrument) // 'GAC-' // trim(platform) // trim(file_version) // trim(suffix_target)

     if (move_L2) then

        command_line = "mv -f " // trim(directory) // trim(dir) // "/" // trim(sourceprimary) // " " // trim(directory) // trim(dir) // "/" // trim(finalprimary)
        finalPrimaryFullPath = trim(directory) // trim(dir) // "/" // trim(finalprimary)
        call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
        write(*,*)  "L2 output file path = ", trim(directory) // trim(dir) // "/" // trim(finalprimary)

     else

        write(12,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"
        write(13,*) """" // trim(directory) // trim(dir) // "/" // trim(sourcesecondary) // """"
        write(14,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"

     endif

  endif

  if (trim(adjustl(instrument)) .eq. 'MODIS' .or. trim(adjustl(instrument)) .eq. 'modis') then

     !MOD021KM.A2008172.1330.006.2012244174154.bspscs_000500706390.hdf
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
     sourcesecondary = trim(adjustl(dri_file(cut_off_head:cut_off_tail-1))) // suffix_source_secondary
     write(*,*) "sourceprimary in wrapper = ", trim(sourceprimary)
     write(*,*) "sourcesecondary in wrapper = ", trim(sourcesecondary)

     cut_off=index(trim(adjustl(dri_file)),yyyymm)
     write(*,*) 'co',cut_off

     !MST day=trim(adjustl(dri_file(cut_off+6:cut_off+7)))
     write(*,*) 'day',day
!postproc_driver_MYD021KM.A2008183.1255.006.2012069031509.bspscs_000500694516.dat
     !MST hour=trim(adjustl(dri_file(cut_off+9:cut_off+10)))
     hour=trim(adjustl(dri_file(cut_off+35:cut_off+36)))
     write(*,*) 'hour',hour

     min=trim(adjustl(dri_file(cut_off+37:cut_off+38)))
     write(*,*) 'min',min

     !200807tYD0200-ESACCI-L2_CLOUD-CLD_PRODUCTS-MODIS-AQUA-fv2.2.nc
     
     !MST
     cut_off=index(trim(adjustl(string)),'MODIS')
     day=trim(adjustl(string(cut_off-3:cut_off-2)))
     !     output/20080701_MODIS_AQUA_retrie
     
     finalprimary = trim(yyyymm) // trim(day) // trim(hour) // trim(min) // &
          '00-ESACCI-L2_CLOUD-CLD_PRODUCTS-' // trim(instrument) // '-' // &
          trim(platform) // trim(file_version) // trim(suffix_target)

     ! finalsecondary = trim(yyyymm) // trim(day) // trim(hour) // trim(min) // &
     !      '00-ESACCI-L2_CLOUD-CLD_SECONDARY_PRODUCTS-' // trim(instrument) // 'GAC-' // &
     !      trim(platform) // trim(file_version) // trim(suffix_target)

     if (move_L2) then

        command_line = "mv -f " // trim(directory) // trim(dir) // "/" // trim(sourceprimary) // " " // trim(directory) // trim(dir) // "/" // trim(finalprimary)
        finalPrimaryFullPath = trim(directory) // trim(dir) // "/" // trim(finalprimary)
        call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
        write(*,*)  "L2 output file path = ", trim(directory) // trim(dir) // "/" // trim(finalprimary)

     else

        write(12,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"
        write(13,*) """" // trim(directory) // trim(dir) // "/" // trim(sourcesecondary) // """"
        write(14,*) """" // trim(directory) // trim(dir) // "/" // trim(finalprimary) // """"

     endif

  endif

end subroutine create_L2_list_or_file

! 2015-05-20: C. Schlundt
subroutine get_file_version(config_attributes, file_version)

  implicit none
  integer :: i1, i2, n, io_error, nlines, whereis
  character(len=256)  :: config_attributes
  character(len=1024) :: string
  character(len=15)   :: file_version

  ! dummy file_version
  file_version = '-fvX.Y'

  write(*,*) "in get_file_version reading ", trim(config_attributes)

  ! Read number of lines in file
  nlines = 0
  open(unit=141, file=trim(adjustl(config_attributes)), &
       status='old', action='read', iostat=io_error)
  if ( io_error == 0 ) then
     do
        read(141,*,END=10)
        nlines = nlines + 1
     end do
  end if
10 close(141)

  ! Read file and get file_version variable
  open(unit=151, file=trim(adjustl(config_attributes)), &
       status='old', action='read', iostat=io_error)
  if ( io_error == 0 ) then
     do n = 1, nlines
        read(151,*) string
        !write(*, 200) trim(string)
        whereis = index(trim(string), 'file_version=')
        if (whereis .ne. 0 ) then
           !write(*,*) 'WHEREIS', whereis, trim(string)
           i1 = scan(trim(string), "'")
           i2 = scan(trim(string), "'", back=.true.)
           !write(*,*) i1, i2, trim(string(i1+1:i2-1))
           file_version = '-fv'//trim(string(i1+1:i2-1))
           write(*,*) 'in get_file_version:  file_version is = ', trim(file_version)
           exit
        end if
     end do
  end if
  close(151)

200 format(a2048)
  return
end subroutine get_file_version
