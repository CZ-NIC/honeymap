use strict;
use warnings;
use LWP::UserAgent;
use JSON;
use Data::Dumper;
use IO::Handle;

my $ua = LWP::UserAgent->new(ssl_opts => { verify_hostname => 1 });
my $url='https://www.virustotal.com/vtapi/v2/file/report';
my $key='apikey';

my %report = ();

open VT, "<", "/opt/honeymap/geoloc/virustotals" or die $!;
open REPORT, ">", "/opt/honeymap/geoloc/malware_report" or die $!;
REPORT->autoflush;

while(<VT>) {
    chomp $_;
    my @line = split /,/, $_;

    my $time = $line[0];
    my $sip = $line[1];
    my $sport = $line[2];
    my $dip = $line[3];
    my $dport = $line[4];
    my $link = $line[5];

    my ($hash) = $link =~ /query=(.*)$/;

    if(!$report{$hash}) {
        print $hash . "\n\n";

        my $response = "";
        my $successful = 0;
        while (!$successful) {
            $response = $ua->post( $url,
                ['apikey' => $key,
                 'resource' => $hash]
              );

            if (!$response->is_success or $response->status_line =~ /^204/ ) {
                print "ERROR: " . $response->status_line . "\n";
                sleep 10;
            }
            else {
                print "is successful\n";
                $successful = 1;
            }
        }

        my $results = $response->content;
        print "we got results";

        my $json = JSON->new->allow_nonref;   
        my $decjson = $json->decode( $results) or print $results;
        $report{$hash} = $decjson->{'scans'}->{'AVG'}->{'result'} // 'unknown';

        sleep 10;
    }

    print "we got here\n";
    print REPORT "$time,$sip,$sport,$dip,$dport,$report{$hash},$link\n";
}

close VT;
close REPORT;
