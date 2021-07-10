#!/usr/bin/perl

#  The above path needs to point to your perl installation

#  Modules - DBI contains the PostgreSQL module Pg.
use Getopt::Long;
use File::Temp  qw/ tempfile tempdir /;
use File::Basename;
use DBI;
use warnings;

# use strict;

my ($progname) = ($0 =~ m#([^/]+)$#);  # get the name of this program

my $usage = "
Usage:  $progname [-h] [-v] [--user=<dbuser>] [--host=<hostname>]
                  [--port=<#>] [--passwd=<password>] [--header] 
                  [--to=<file>] shapefile
                  
where
   -h                    Help, prints this menu
   -v                    Verbose output
   --user=<username>    Provide the name of the user to access the VIMSDB. 
                           Default:  vimsread
   --host=<hostname>    Provide the name of the host where the VIMS database is
                           located.  If not provided, defaults to localhost.
   --port=<#>           Provide a port number to use instead of the default for
                           the VIMSDB daabase (typically a PostgreSQL).
                           Default: 3309
   --passwd=<password>  Specify the password to the VISMDB database.  Note this is
                           typically an unsafe practice so it is suggested that
                           users apply alternatives to provide this info.
                           Default: public
   --header             Select the first row of the output file to have the
                           column names (a header)
   --to=<file>          Optional output filename to write results to.

example -> ./vimsdb_shapefile_query.pl --to=myoutput.csv shapefile
";      

#####################################################################
#  Author:  Jason Soderblom, MIT 
#  Date:    2014-03-04
#           Copied from vimsdb_query.pl, origially written by Kris Becker, USGS, Flagstaff and
#           modified on 2013-06-20 to include the Titan spatial reference (needed now that the database
#           include a spatial reference). This is hard coded to SRID = 60600, the Titan 2000
#           spatial reference, see http://spatialreference.org/ref/?search=titan&srtext=Search
#
#           
#####################################################################
my $help = '';          # Help option

# Get options
my $opterrs = GetOptions ( "h"          => \$help,
                           "v"          => \$verbose,
                           "dryrun"     => \$dryrun,
                           "user=s"     => \$user,
                           "host=s"     => \$host,
                           "port=n"     => \$port,
                           "passwd=s"   => \$passwd,
                           "header"     => \$header,
                           "to=s"       => \$to
                           );

#  Do some sanity checks
die "$usage\n" if (!$opterrs);
die "$usage\n" if ($help);
die "$usage\n" if (@ARGV != 1);

#  Input shapefile parameters
my $shapefile = $ARGV[0];

# $dryrun = 1;  # If testing
$verbose = 1 if ($dryrun);  #  --dryrun was an arg but not fully implemented

#  Ensure temp directory for processing needs
$tmpdir = $ENV{PWD} if (!$tmpdir);
$opath  = $ENV{PWD} if (!$opath);
#print "009183290183902189d0321890382190389201839018930289138290";
#  Convert shape file to simple WKT format using ogr2ogr
$shapefile_wkt = "temp_wkt_file.csv";
unlink $shapefile_wkt if (-e $shapefile_wkt);

$cmd = "ogr2ogr -f CSV -overwrite $shapefile_wkt $shapefile -lco GEOMETRY=AS_WKT";
print "Creating WKT file from shapefile\n" if ($verbose);
print "$cmd\n" if ($verbose);
#print "hereereereerererere";
$result = system($cmd);
#print "hereereereerererere";
if ($result != 0)
  {
    print "[ERROR] ogr2ogr failed\n";
    exit;
  }

#  Read shape from wkt
#print "hereereereerererere";
open(FILE, $shapefile_wkt) or die "Can't read file $shapefile_wkt\n";  
@shapes = <FILE>; 
close (FILE);  
#print "hellohelhoehpresokhropeskhopreakhopreakhpkaeophke";
# Establish defaults for parameters
$to = "/dev/null" if (!$to || $dryrun);
$user = "vimsread" if (!$user);
$host = "localhost" if (!$host);
$port = "3309" if (!$port);
$passwd = "public" if (!$passwd);

#  Ok now check PostgreSQL connections
my $pgparms = "";
$pgparms .= ";host=${host}";
$pgparms .= ";port=$port";
my $pgsql = DBI->connect("DBI:Pg:dbname=vimsdb${pgparms}",$user, $passwd)
            or die "Could not connect to PostgreSQL database.\n";
#print footprint
#  Set up VIMSDB query.  Can be any select form you want.  ? indicates
#  substition.  See the prepare/binders code below.
#print "here-=2394=2-39-=249-3294-=24";
my $pgstm = 'select name, latitude, longitude, 
             phase, incidence, emission, distance, lineres, sampres, spectrum
             from vims_trial where ST_Contains(?, footprint)';
            #  spectrum[65] as band_65, 
            #  spectrum[66] as band_66, 
            #  spectrum[67] as band_67, 
            #  spectrum[68] as band_68, 
            #  spectrum[69] as band_69, 
            #  spectrum[70] as band_70, 
            #  spectrum[71] as band_71, 
            #  spectrum[72] as band_72, 
            #  spectrum[73] as band_73, 
            #  spectrum[74] as band_74, 
            #  spectrum[75] as band_75, 
            #  spectrum[76] as band_76, 
            #  spectrum[77] as band_77, 
            #  spectrum[78] as band_78, 
            #  spectrum[239] as band_239, 
            #  spectrum[240] as band_240, 
            #  spectrum[241] as band_241, 
            #  spectrum[242] as band_242, 
            #  spectrum[243] as band_243, 
            #  spectrum[244] as band_244, 
            #  spectrum[245] as band_245, 
            #  spectrum[246] as band_246, 
            #  spectrum[247] as band_247, 
            #  spectrum[248] as band_248, 
            #  spectrum[249] as band_249, 
            #  spectrum[250] as band_250, 
            #  spectrum[251] as band_251, 
            #  spectrum[252] as band_252, 
            #  spectrum[253] as band_253, 
            #  spectrum[254] as band_254, 
            #  spectrum[255] as band_255, 
            #  spectrum[256] as band_256 
            #  from vims_trial 
            #  where ST_Contains(?, footprint)";
#my $pgstm = "select * from vims_trial where ST_Contains(?, footprint)";
print $pgstm
#  Open the output file
print "Creating output file ${to}\n" if ($verbose);
open (OUT, ">>${to}") or die "Could not create output file --to=${to}\n";

my $nshapes = @shapes - 1;
$ind = 1;

#  Get position of ? in statement for replacement
my $qindex = index($pgstm, '?');
print "Q index = $qindex\n" if ($verbose);

while ($ind <= $nshapes)
  {

  my $shape_i = "ST_GeomFromEWKT('SRID=60600;" . substr($shapes[$ind], 1, -4) . "')";
  #print $shape_i;
  
  #print "herehereherehrehrewhrewiuhrafi;hgueiahwgieu;awhgiwauhgewahgiuehwau;igeh";
  my $qstm = $pgstm;
  my $qt = substr($qstm, $qindex, 1, $shape_i);
  print "Statement: $qstm\n" if ($verbose);

  #  Set up prepared statements for the databases
  my $psth = $pgsql->prepare("${qstm}");

  #  Now set up the VIMSDB query
  print "\nSearching for points within shape $ind of $nshapes\n" if ($verbose);
  $psth->execute or die "Query error occurred - terminated: $DBI::errstr!\n";

  #  Print header in CSV format to output file if requested
  my $columns = join(',', @{ $psth->{NAME_lc} });
  print "$columns\n" if ($verbose);
  print OUT "$columns\n" if ($header);

  $nrows = 0;
  while (@vrow = $psth->fetchrow_array)
    {
    $nrows ++;
    #  Make CSV format
    my $values = join(',', @{vrow} );
    print "$values\n" if ($verbose);
    print OUT "$values\n";
    }
  
  $ind +=1;
  }

print "Total VIMS points found: ${nrows}\n";
close(OUT);

#  Disconnect from database
$pgsql->disconnect;
exit(0);
