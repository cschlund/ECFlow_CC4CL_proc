subroutine build_inventory(log_dir,out_dir,jid,&
     & instrument,platform,month,year,&
     & inventory_file_pre,inventory_file_liq,inventory_file_ice,inventory_file_post,mytask,ntasks)

  implicit none

  integer :: ntasks,mytask

  character(len=512) :: jid,log_dir,out_dir
  character(len=15) :: instrument,platform  
  character(len=4) :: year
  character(len=2) :: month

  character(len=256) :: inventory_file_pre,inventory_file_liq,inventory_file_ice,inventory_file_post
  character(len=1536) :: command_line

  integer :: estat,cstat
  character(len=1024) :: cmsg


  !set up inventory file names
  write(*,*) 'INV: define files'
  inventory_file_pre=trim(adjustl(log_dir))//&
       & '/process_single_day_'//trim(adjustl(year))//trim(adjustl(month))//&
       & '_'//trim(adjustl(instrument))//'_'//trim(adjustl(platform))//'_'//&
       & trim(adjustl(jid))//'.pre.lst'
  write(*,*) 'pre',trim(adjustl(inventory_file_pre))

  inventory_file_liq=trim(adjustl(log_dir))//&
       & '/process_single_day_'//trim(adjustl(year))//trim(adjustl(month))//&
       & '_'//trim(adjustl(instrument))//'_'//trim(adjustl(platform))//'_'//&
       & trim(adjustl(jid))//'.liq.lst'
  write(*,*) 'liq',trim(adjustl(inventory_file_liq))

  inventory_file_ice=trim(adjustl(log_dir))//&
       & '/process_single_day_'//trim(adjustl(year))//trim(adjustl(month))//&
       & '_'//trim(adjustl(instrument))//'_'//trim(adjustl(platform))//'_'//&
       & trim(adjustl(jid))//'.ice.lst'
  write(*,*) 'ice',trim(adjustl(inventory_file_ice)) 

  inventory_file_post=trim(adjustl(log_dir))//&
       & '/process_single_day_'//trim(adjustl(year))//trim(adjustl(month))//&
       & '_'//trim(adjustl(instrument))//'_'//trim(adjustl(platform))//'_'//&
       & trim(adjustl(jid))//'.post.lst'
  write(*,*) 'post',trim(adjustl(inventory_file_post))

  ! inventory_file_post_secondary=trim(adjustl(log_dir))//&
  !      & '/process_single_day_'//trim(adjustl(year))//trim(adjustl(month))//&
  !      & '_'//trim(adjustl(instrument))//'_'//trim(adjustl(platform))//'_'//&
  !      & trim(adjustl(jid))//'.post_secondary.lst'
  ! write(*,*) 'post',trim(adjustl(inventory_file_post_secondary))   

  !erase any existing files
  command_line='rm -rf '//trim(adjustl(inventory_file_pre))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='rm -rf '//trim(adjustl(inventory_file_liq))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='rm -rf '//trim(adjustl(inventory_file_ice))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='rm -rf '//trim(adjustl(inventory_file_post))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  ! command_line='rm -rf '//trim(adjustl(inventory_file_post_secondary))
  ! call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  ! write(*,*) trim(adjustl(command_line))

  !determine number of files and write into inventory
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/ -mindepth 1 -maxdepth 1 -type d | wc -l >> '//trim(adjustl(inventory_file_pre))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/ -mindepth 1 -maxdepth 1 -type d | wc -l >> '//trim(adjustl(inventory_file_liq))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/ -mindepth 1 -maxdepth 1 -type d | wc -l >> '//trim(adjustl(inventory_file_ice))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/ -mindepth 1 -maxdepth 1 -type d | wc -l >> '//trim(adjustl(inventory_file_post))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  ! command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/ -mindepth 1 -maxdepth 1 -type d | wc -l >> '//trim(adjustl(inventory_file_post_secondary))
  ! call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  ! write(*,*) trim(adjustl(command_line))

  !fill inventory files
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/*/preproc_driver_*.dat -maxdepth 3 -type f | sort >> '&
       & //trim(adjustl(inventory_file_pre))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/*/mainproc_driver_*WAT.dat -maxdepth 3 -type f | sort >> '&
       & //trim(adjustl(inventory_file_liq))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/*/mainproc_driver_*ICE.dat -maxdepth 3 -type f | sort >> '&
       & //trim(adjustl(inventory_file_ice))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/*/postproc_driver_*.dat -maxdepth 3 -type f | sort >> '&
       & //trim(adjustl(inventory_file_post))
  call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  write(*,*) trim(adjustl(command_line))
  ! command_line='find '//trim(adjustl(out_dir))//'/*' //trim(adjustl(jid))// '/*/postproc_driver_*.dat -maxdepth 3 -type f | sort >> '&
  !      & //trim(adjustl(inventory_file_post_secondary))
  ! call execute_command_line(trim(adjustl(command_line)),wait=.true.,exitstat=estat,cmdstat=cstat,cmdmsg=cmsg)
  ! write(*,*) trim(adjustl(command_line))
  
end subroutine build_inventory
