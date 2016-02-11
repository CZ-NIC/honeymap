use strict;
use warnings;

my $date=$ARGV[0];
my $day_before=$ARGV[1];

open VT, "<", "/opt/honeymap/geoloc/" . $date . ".csv" or die $!;
my %data = ();

for (my $i = 0; $i<24; $i++) {
    $data{$i} = {};
}

while(<VT>) {
    my $row = $_;
    my ($countrycode, $hour) = $row =~ /^(\w+) [0-9-]+ (\d{2}).*$/;
    my $cet_hour = $hour + 0;

    # GMT magic. now all times are in CET, this is left for historical reasons
    # following GMT magic works for CEST
    if ($row =~ /GMT/) {
        if ($row =~ /${day_before} 2[23].*GMT/) {
            $cet_hour = $hour - '22';
        }
        # date, and hour is from 00 to 21
        elsif ($row =~ /${date} ([01]|2[01]).*GMT/) {
            $cet_hour = $hour + '2';
        }
    }

    if (!$data{$cet_hour}{$countrycode}) {
        $data{$cet_hour}{$countrycode} = 1;
    }
    else {
        $data{$cet_hour}{$countrycode}++;
    }
}
close VT;


use JSON;
open my $write, ">", "/opt/honeymap/client/input/" . $date . ".json" or die $!;
print $write encode_json(\%data);
print $write "\n";
close $write;
