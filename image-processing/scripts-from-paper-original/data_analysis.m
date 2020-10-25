%   28.11.2017, MATLAB script for data processing
%   Script #3 in "Measuring dorsoventral pattern and morphogen signaling activity profiles in the growing neural tube"
%   in Methods of Molecular Biology
%   Anna Kicheva, Marcin Zagorski

%%clearing workspace and figures
clear;                              %clears workspace

%%user defined variables (modify here, path2profiles, etc.)
path2profiles = uigetdir('','Select folder with quantified fluorescent intensity profiles');        %user specfied path to Fiji script output files
%path2profiles = 'profiles_FI';          %fix the path to Fiji results when redoing analysis many times
smooth_window = 5;                      %smoothing window in microns
ch_ok = [2 3 4];                        %MODIFY IF NEEDED, select channels to be analyzed; in our dataset channel 1 (Dapi) is used to specify ROIs and not considered later
excludeV_bg = 0.1; excludeD_bg = 0.9;   %excludes 10% points on each side of DVposition for estimating bacground
L0 = 100; tau0 = 10;                    %starting values for exponential fit L0*exp(t/tau0)
time_intervals = 10:20:70;              %3 time intervals (each 20h); use for small sample to test the script; adjust intial and end time if needed
%time_intervals = 0:10:70               %7 time intervals (each 10h); use when more data points are available
dv_relstep = 0.01;                      %DV relative positions increase step from 0 to 1; should not be lower than 1/(number of pixels in any image)
cutV = 0.05; cutD = 0.95;               %excluding boundary regions, by default 5% on each side; used for consolidating mean and maximizing R2
R2_threshold = 0.5;                     %discard profiles with R^2 < R2_threshold

%%flags used to switch off parts of the script
flag_plotting   = 1;                    %makes plots on the way
flag_restaging  = 1;                    %use developmental time restaging
flag_discarding = 1;                    %runs discarding procedure
flag_diagnostic = 1;                    %runs extra checks on the way

%%other variables (calculated from the user defined variables)
col_ok = ch_ok + 2;                     %columns corresponding to selected channels
nCH = numel(ch_ok);                     %number of channels to be analyzed
%nF                                     %number of raw profiles; defined below through number of imported files
nBIN = numel(time_intervals) - 1;       %number of time intervals (bins)
DVrelative = (0:dv_relstep:1)';         %relative DV position (same for all profiles)
av_bin_time = zeros(nBIN,1);            %centers of the time intervals
for i = 1:nBIN
    av_bin_time(i) = (time_intervals(i)+time_intervals(i+1))/2;
    av_bin_time_str{i} = strcat(num2str(av_bin_time(i)),'h');       %used for legend when plotting is ON
end

%%importing files
files = dir(strcat(path2profiles,'/','*.txt'));    %getting file list from the folder
nF = length(files);                            %stores number of files, by default nF is also the number of raw profiles
if nF == 0
    fprintf('ERROR. No files imported.\n');      %prints error message when no files were found
    return                                       %stops script               
end
for i = 1:nF  
  filenames{i,1}    = files(i,1).name;                                 %getting file name list
  temp = importdata(strcat(path2profiles,'/',files(i).name), '\t', 1);     %importing data from the folder
  profiles_raw{i}   = temp.data;                 %raw profiles
  profiles_label{i} = temp.colheaders;           %column headers (row_id, DV_position (um), ch1, ch2, ...)  
end

clear files temp;                               %removing unnecessary variables
profiles_label = profiles_label';               %column headers
profiles_raw   = profiles_raw';                 %imported profiles

%%determining somite stage from file name and assigning ss time
ss_data = NaN*ones(nF,1);                       %creates empty column for somite stage; ss_time stores somite stage time
for i = 1:nF 
    pos = strfind(filenames{i},'ss');           %finidng 'ss' substring in the filename; designed for only one 'ss' is in the filename
    str = filenames{i}(pos-2:pos-1);
    if str(1) == '0'                            %checks for 01ss to 09ss for somite stages 1 to 9
        ss_data(i) = str2num(str(2));           
    else
        ss_data(i) = str2num(str);
    end
end
ss_time = 2* ss_data;                           %time from somite stage = 2 * somite_stage

%%getting DV length in microns
dv_length = NaN*ones(nF,1);                     %creates empty column for DV length;
for i = 1:nF
    dv_length(i) = profiles_raw{i}(end,2);
end

%%sorting profiles and related data for increasing dv_length; optional but helpful for time binning
if flag_restaging == 1
    [dv_length, I] = sort(dv_length);
    ss_time = ss_time(I);
    ss_data = ss_data(I);
    filenames = filenames(I);
    profiles_raw = profiles_raw(I);
    profiles_label = profiles_label(I);
else                                    %use somite stage time for sorting if restaging is off
    [ss_time, I] = sort(ss_time);
    dv_length = dv_length(I);
    ss_data = ss_data(I);
    filenames = filenames(I);
    profiles_raw = profiles_raw(I);
    profiles_label = profiles_label(I);
end

%%getting DV position for all profiles + getting pixel resolution
pix_resolution = NaN*ones(nF,1);                     %creates empty column for pixel resolution; useful when resolution varies between images
for i = 1:nF
    DVposition{i} = profiles_raw{i}(:,2);
    pix_resolution(i) = dv_length(i)/(numel(DVposition{i}) - 1);
end
DVposition = DVposition';

%%smoothing profiles over one cell diameter (4-5 um); smoothing window is
%%defined in 'smooth_window' variable
smooth_span = ceil(smooth_window * pix_resolution.^-1); %smoothing span as a number of array indices
for i = 1:nF
    for j = 1:nCH
        profiles_sm{i,j} = smooth( profiles_raw{i}(:,col_ok(j)), smooth_span(i) );
    end
end

%%subtracting background; by default 10% on V and D side is excluded
for i = 1:nF
    dvpV = quantile(DVposition{i},excludeV_bg);
    dvpD = quantile(DVposition{i},excludeD_bg);
    ind  = (dvpV < DVposition{i} & DVposition{i} < dvpD);   %getting indices for background subtraction
    for j = 1:nCH
        bg = min(profiles_sm{i,j}(ind));                    %background as minimum of profile intensity in specified range
        profiles_smbg{i,j} = profiles_sm{i,j} - bg;         %smoothed & background subtracted profiles
    end
end

%%fitting exponential function to dv_length vs ss_time; exp fit is used to restage profiles
if flag_restaging == 1
    fprintf('Restaging: ON\ntime from exp fit\n')
    fexp = fit(ss_time,dv_length,'exp1','StartPoint',[L0, 1/tau0]) %fit exp function
    val_fit = coeffvalues(fexp);                         %get fit parameters (tau is inverse of default Matlab exp1 2nd coeff)  
    L0_fit  = val_fit(1);
    tau0_fit = 1/val_fit(2);
    if flag_plotting == 1
        figure(1); clf reset;
        plot(fexp,ss_time,dv_length, 'ko')                             %PLOT fit and data points 
        %xlim([min(time_intervals) max(time_intervals)]);
        ylabel('DV length ({\mu}m)');
        xlabel('Time_{ss} (h)');
    end
    dv_time = arrayfun(@(L) tau0_fit*log(L/L0_fit), dv_length);     %restaging by appyling inverse of the fit to dv_length
    %plot(fexp,dv_time,dv_length, 'ko')                             %PLOT fit and restaged data points
else
    fprintf('Restaging: OFF\ntime from somite stage\n')
    dv_time = ss_time;                                  %somite stage time is used as a proxy for developmental time
end

%%binning to time intervals
for i=1:nBIN
   if i==1
        bin_ind{1} = (dv_time < time_intervals(2));  %bin_ind{i} indicates which profiles are in i-th time interval; treats first time_interval specially (useful when first time_interval starts at t=0, and some dv_time are negative due to restaging)
   else
        bin_ind{i} = (time_intervals(i) <= dv_time & dv_time < time_intervals(i+1));  %bin_ind{i} indicates which profiles are in i-th time interval
   end
   bin_n(i)   = sum(bin_ind{i});                                                %number of samples per bin  
end

%%checking whether each bin contains at least 1 profile
zero_bins = sum(bin_n == 0);           %number of time intervals containing 0 profiles
if zero_bins > 0
    fprintf('ERROR. There were %d time intervals without any profiles. The script is stopped. Adjust time_intervals if needed.\n',zero_bins);
    fprintf('Number of profiles in consecutive time intervals:\n');
    disp(bin_n)
    return                                       %stops script
end

%%warning pops up when some profiles are outside of time intervals
n_temp_HIGH = sum(time_intervals(nBIN + 1) <= dv_time);             %number of profiles with dv_time greater (or equal) than any time interval
n_temp_LOW =  sum(dv_time < time_intervals(1));                     %number of profiles with dv_time greater (or equal) than any time interval
if n_temp_HIGH > 0
    fprintf('WARNING. Number of profiles later than any time interval: %d. These profiles are NOT analysed. Adjust time_intervals if needed.\n',n_temp_HIGH);
end
if n_temp_LOW > 0
    fprintf('WARNING. Number of profiles preceeding any time interval: %d. These profiles are moved to the 1st time interval. Consider adjusting time_intervals if needed\n',n_temp_LOW);
end

%%DIAGNOSTICS; checking how many profiles were restaged by more than delta_t = 10h
if flag_diagnostic == 1
    delta_t = 10;
    temp = abs(dv_time - ss_time);
    restaged_profiles = sum( temp > delta_t);
    fprintf('Total number of samples %d; %d samples restaged by more than %dh\n',nF, restaged_profiles,delta_t)
    fprintf('Restaging rate %4.3f\n',restaged_profiles/nF)
end

%%rescaling DVposition to relative DVposition; this is independent of restaging procedure; linear interpolation might undersample the original data -- use smoothing step or alternative spatial binning
for i = 1:nF
    for j = 1:nCH
        profiles_rs{i,j} = interp1(DVposition{i}, profiles_smbg{i,j}, DVrelative * dv_length(i));  % interpolates profiles, so they can by compared at the same rel DV positions
    end
end

%%mean profile calculation for each time interval
for i = 1:nBIN
    for j = 1:nCH
        bin_prof = horzcat(profiles_rs{ bin_ind{i}, j});    %all profiles in the i-th bin for j-th channel
        profiles_mean0{i,j} = mean(bin_prof,2);             %mean profile for i-th and j-th channel
    end
end

%j=1; plot(DVrelative,profiles_mean{1,j},DVrelative,profiles_mean{2,j},DVrelative,profiles_mean{3,j}) %PLOT mean for the i-th channel and consequtive time intervals

%%estimating background of the mean profiles & subtracting from profiles
dvpV = quantile(DVrelative, excludeV_bg);
dvpD = quantile(DVrelative, excludeD_bg);
ind  = (dvpV < DVrelative & DVrelative < dvpD);   %getting indices for background subtraction

bg_mean = NaN*ones(nBIN, nCH);                    %array that stores background for the mean profile
for i = 1:nBIN
    for j = 1:nCH
        bg_mean(i,j) = min(profiles_mean0{i,j}(ind));        %filling bg_mean array with background of the mean profiles
    end
end

for i = 1:nBIN
    for j = 1:nCH
        bin_prof = horzcat(profiles_rs{ bin_ind{i}, j});    %all profiles in the i-th bin for j-th channel
        profiles_rsbg{i,j} = bin_prof - bg_mean(i,j);       %all profiles for i-th and j-th channel with background subtracted
        profiles_meanbg{i,j} = mean(profiles_rsbg{i,j},2);  %mean recalculated for profiles in the i-th and j-th channel
    end
end

%%excluding boundary regions
ind  = (cutV <= DVrelative & DVrelative <= cutD);           %excluding boundary regions; keeps edges for convenience
DVrelative_c = DVrelative(ind);
for i = 1:nBIN
    for j = 1:nCH
        profiles_rsbgc{i,j} = profiles_rsbg{i,j}(ind,:);       %excluding boundary regions for i-th and j-th channel with excluded boundaries
        profiles_meanbgc{i,j} = mean(profiles_rsbgc{i,j},2);   %mean recalculated for profiles in the i-th and j-th channel with excluded boundaries
    end
end

%%consolidating mean and discarding outliers
resfun = @(x,xdata)x(1)*xdata;                              %used in one-parameter minimization of profile deviation from the mean
%resfun = @(x,xdata)x(1)*xdata + x(2);                      %used in two-parameter minimization of profile deviation from the mean
opts = optimset('Display','off');                           %suppress message output from lsqcurve fit

%%initializing R2_maximization
profiles_A = profiles_rsbgc;                %stores rescaled profiles
n_discarded = 0;                            %counts discarded outliers
for i = 1:nBIN                              %i-th time interval
    for j = 1:nCH                           %j-th channel
        A_tab{i,j} = ones(1,bin_n(i));      %initializng array for profile rescaling factors
        R2_tab{i,j} = NaN*ones(1,bin_n(i)); %initializng array for R^2
        R2_ind{i,j} = [1:1:bin_n(i)];       %indices for good profiles
    end
end

if flag_discarding == 1
    fprintf('R2 maximization and discarding procedure: ON\n');
    fprintf('Iteration 1\n')
    R2_stop_iteration_thr = 2;              %2 is ok; number of iteration steps for a given time interval and channel to be performed when all profiles with low R2 are discrded;
    R2_stop_tab = zeros(nBIN, nCH);         %stores number of iterations without discarding profiles with low R2
    R2_stop_all = (R2_stop_iteration_thr)*nBIN*nCH; %stops discarding outliers in all bins and channels

    z_iter = 1;
    bg_Amean = NaN*ones(nBIN, nCH);                    %array that stores background for the mean profile with discarded outliers
    while sum( R2_stop_tab(:) ) < R2_stop_all
        z_iter = z_iter +1;
        fprintf('Iteration %d\n',z_iter)
        for i = 1:nBIN                  %i-th time interval
            for j = 1:nCH               %j-th channel
                if R2_stop_tab(i,j) < R2_stop_iteration_thr     %stopping condition
                    %reestimating mean profile and its background with discarded R2 outliers
                    good_ind = R2_ind{i,j};
                    profiles_mean{i,j} = mean( profiles_rsbgc{i,j} (:,good_ind),2);  %use non-rescaled profiles to recalculate mean (otherwise drop in intensity)
                    bg_Amean(i,j) = min( profiles_mean{i,j} );                       %filling bg_mean array with background of the mean profiles
                    prof_mean = profiles_mean{i,j} - bg_Amean(i,j);                  %mean profile with background subtracted 
                    for k = 1:numel(good_ind)      %k-th profile in i-th time interval for good_ind
                        prof_temp = profiles_A{i,j}(:,good_ind(k)) - bg_Amean(i,j);  %subtracting mean background for individual profiles in the bin
                        [A, SSres] = lsqcurvefit(resfun, [1], prof_temp, prof_mean, [], [], opts);  %fitting individual profiles to the mean profile
                        SStot = sum( (prof_mean - mean(prof_mean)).^2 );
                        R2 = 1 - SSres/SStot;                                        %calcluating R2   
                        R2_tab{i,j}(good_ind(k))= R2;                                %updates only good profiles
                        A_tab{i,j}(good_ind(k)) = A * A_tab{i,j}(good_ind(k));              %rescaling factors for intensity, updating A_tab with every iteration
                        profiles_A{i,j}(:,good_ind(k)) = A*profiles_A{i,j}(:,good_ind(k));  %rescaled profiles
                    end
                    R2vec = R2_tab{i,j}(good_ind);    %only R2 for good_ind is checked  
                    R2_min = min(R2vec);              %the lowest R2 for a given time-interval and channel
                    %R2_min = R2_threshold;           %all R2 below threshold in one iteration -- can spped up computation for very large datasets
                    if R2_min < R2_threshold
                        ind = R2vec > R2_min;         %indices for all profiles with R2 > the lowest R2  
                        %n_discarded = n_discarded + 1;     %calculated after discarding is finished
                    else
                        ind = R2vec >= R2_threshold;        %if all profiles not lower than R2_threshold, all are selected
                        R2_stop_tab(i,j) = R2_stop_tab(i,j) + 1;    %increases by 1 for every iteration with no discarded profiles
                    end
                    good_ind_new = good_ind( find( good_ind.*ind > 0) );
                    R2_ind{i,j} = good_ind_new;       %updating R2_ind
                end
            end
        end
    end
    %once discarding is finished, recalculate mean for the rescaled profiles
    for i = 1:nBIN                  %i-th time interval
            for j = 1:nCH           %j-th channel
                good_ind = R2_ind{i,j};
                profiles_Amean{i,j} = mean( profiles_A{i,j}(:,good_ind),2);  %use non-rescaled profiles to recalculate mean (otherwise drop in intensity)
                bg_Amean(i,j) = min( profiles_Amean{i,j} );                       %filling bg_mean array with background of the mean profiles
                profiles_Amean{i,j} = profiles_Amean{i,j} - bg_Amean(i,j);
                for k = 1:numel(good_ind)      %k-th profile in i-th time interval for good_ind
                        profiles_A{i,j}(:,good_ind(k)) = profiles_A{i,j}(:,good_ind(k)) - bg_Amean(i,j);    %subtracting mean background for each profile
                end
            end
    end
else                %flag_discarding == 0
    fprintf('R2 maximization and discarding procedure: OFF\n');
    for i = 1:nBIN                  %i-th time interval
        for j = 1:nCH               %j-th channel
            profiles_mean{i,j} = mean( profiles_rsbgc{i,j},2);  %calculating mean profile;
            profiles_Amean{i,j} = profiles_mean{i,j};           %for consistency when plotting flag is 1;
        end
    end
end

%%Logical indexing of good profiles (can be used for additional analysis)
for i = 1:nBIN                  %i-th time interval
    for j = 1:nCH               %j-th channel
        R2_ok{i,j} = zeros(1,bin_n(i));
        good_ind = R2_ind{i,j};
        R2_ok{i,j}(good_ind) = 1; %indices for good profiles as logical values (1 - profile is ok; 0 - profile discarded)
        n_discarded = n_discarded + bin_n(i) - numel(good_ind);
    end
end

%%Some statistics and plotting
n_total = sum( bin_n )* nCH;            %should be equal nF*nCH, unless some profiles were not used in the binning procedure
if(n_total ~= nF*nCH)
    fprintf('Profiles discarded before consolidating mean: %d\n',nF*nCH - n_total)
end
fprintf('Total profiles %d, discarded profiles %d \n',n_total,n_discarded)
fprintf('Discarding rate %4.3f\n',n_discarded/n_total)

if flag_plotting == 1
    figure(2); clf reset;
    for i = 1:nBIN                  %i-th time interval
        for j = 1:nCH               %j-th channel
            subplot( nBIN, nCH,(i-1)*nCH + j);
            plot(DVrelative_c,profiles_meanbgc{i,j},'k',DVrelative_c,profiles_mean{i,j},'r',DVrelative_c,profiles_Amean{i,j},'b') %PLOT compares mean with all profiles (black), without discarded (red) and rescaled (blue)
            title(['Channel ',int2str(j),', Time ',av_bin_time_str{i}],'FontWeight','normal')
            ymax = max( profiles_meanbgc{i,j} )*1.1;
            if j == 1
                ylabel('Intensity (a.u.)');
            end
            if i == nBIN
                xlabel('Rel DV pos');
            end
            axis([0 1 -0.05*ymax ymax])
            pbaspect([1 1 1])
            if i == 1 && j ==1
                legend({'all profiles','non-discarded','rescaled'},'Location','northwest')
                legend('boxoff')
            end
        end
    end
end

%%Normalizing profiles in a given channel by a common factor, such that over time max mean profile equals to 1
max_profiles = NaN*ones(nBIN, nCH);         %max intensity for all good profiles per time interval and channel
max_channel  = NaN*ones(1, nCH);            %then max for a given channel is selected
for i = 1:nBIN
    for j = 1:nCH
        max_profiles(i,j) = max( profiles_Amean{i,j} );        
    end
end

for j = 1:nCH
        max_channel(j) = max( max_profiles(:,j));    %max for a given channel
end

for i = 1:nBIN
    for j = 1:nCH
        profiles_N{i,j} = profiles_A{i,j} / max_channel(j);             %all profiles are normalized
        profiles_Nmean{i,j} = profiles_Amean{i,j} / max_channel(j);     %mean is only for good profiles
    end
end

%%Plotting
if flag_plotting == 1
    figure(3); clf reset;
    for j = 1:nCH               %j-th channel
            subplot( 1, nCH, j);
            hold on
            for i = 1:nBIN
                plot(DVrelative_c,profiles_Nmean{i,j}) %PLOT compares normalized mean for different time intervals
                axis([0 1 -0.05 1.05])
                pbaspect([1 1 1])
            end
            title(['Channel ',int2str(j),', mean profile'],'FontWeight','normal')
            if j == 1
                ylabel('Intensity (a.u.)'); 
            end
            xlabel('Rel DV pos');
            if j == 1
                legend(av_bin_time_str,'Location','northwest')
                legend('boxoff')
            end
    end
end       

%%DIAGNOSTICS; getting rescaling factors for non-discarded profiles
if flag_diagnostic == 1
    vtemp = NaN*ones(nBIN,nCH,2);
    for i = 1:nBIN                  %i-th time interval
        for j = 1:nCH               %j-th channel
            good_ind = R2_ind{i,j};
            temp = A_tab{i,j}(good_ind);
            vtemp(i,j,:) = [mean(temp) std(temp)];  %mean and std dev of rescaling factors for i-th bin and j-th channel; consider taking mean and std of log(temp)
            %vtemp(i,j,:) = [mean(log(temp)) std(log(temp))];  %the same with log()
        end
    end     
    for j = 1:nCH               %j-th channel
            mA = mean(vtemp(:,j,1));
            mAstd = mean(vtemp(:,j,2));
            fprintf('Channel %d, mean rescale factor %4.3f +/- %4.3f\n',j,mA,mAstd)
    end
end

%%clearing temporary variables; comment out for debugging
clear pos str i j k I col_ok dvpD dvpV ind bg val_fit bin_prof good_ind good_ind_new opts prof_temp prof_mean mA mAstd mAvar temp_data A temp ymax z_iter SSres SStot R2_stop_all R2_stop_tab R2_stop_iteration_thr
clear R2 R2_min R2vec av_bin_time

                                                    