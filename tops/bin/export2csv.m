
% ps_plot('v-dao', 'a_linear', 'ts');

% Export to scv file
file_name = 'stamps_asc_lunana_ps_17_19tt.csv';
% after the plot has appeared magically, set radius and location by clicking into the plot
load parms.mat;
ps_plot('v-dao', 'a_linear', -1);
load ps_plot_v-dao.mat;
lon2_str = cellstr(num2str(lon2));
lat2_str = cellstr(num2str(lat2));
lonlat2_str = strcat(lon2_str, lat2_str);
lonlat_str = strcat(cellstr(num2str(lonlat(:,1))), cellstr(num2str(lonlat(:,2))));
%ind = ismember(lonlat_str, lonlat2_str);
ind = ismember(lonlat2_str, lonlat_str);
ind_count = sum(ind(:)==1);
disp = ph_disp(ind);
disp_ts = ph_mm(ind,:);
export_res = [lon2 lat2 disp disp_ts];
metarow = [ref_centre_lonlat NaN transpose(day)-1];
k = 0;
export_res = [export_res(1:k,:); metarow; export_res(k+1:end,:)];
export_res = table(export_res);
writetable(export_res, file_name)