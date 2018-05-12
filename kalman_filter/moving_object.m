% In this example, we have an object moving with a constant speed of 1.
% The system does not involve any control logic. 

F = [1,1 ; 0,1];% the transformation matrix is for xt = x+1 = previous position + speed
P = [1,1 ; 1,1]; % the covariance matrix is 1 in the beginning
x = [1; 1]; % our model is a matrix of the form [position; speed]

R = [0.1,0.1 ; 0.1,0.1]; % Sensor standard deviation; constant in the system
H = [1,0;0,1]; % sensor to model data transformation. Does nothing.

space = [1:1:20];
space_len = length(space);
meas_noise = noise(space_len,'white')';

% the measurements are noisy. They do not represent the actual positions of the train
% the second row represents that constant speed.
measurements = [space.+meas_noise; repmat(1, 1, space_len)];

predicted_movements = [x(1)];
for t = space(2:end)
  % Prediction
  xt = F*x;
  Pt = F*P*F';
  
  zt = measurements(:,t);
  %Correction
  K = Pt*H'*1/(H*Pt*H' + R);
  x = xt + K * (zt -H*xt);
  P = (1 - K)*H*Pt;
  
  % compute and multiply pdfs
  % Given the sensor data and our prediction, see what the most likely position is
  pred_pdf = normpdf(space, x(1), P(1,1));
  sense_pdf = normpdf(space, zt(1), R(1,1));
  fused = pred_pdf .* sense_pdf;
  [m, pos] = max(fused);
  
  % add the most likely position to the list of predicted movements
  predicted_movements(end + 1) = pos;
endfor

figure(1);
plot(space, measurements(1,:), ";Sensor Measurement;", ...
  space, predicted_movements, "r*;Predicted Movement;", ...
  space, space, ";Actual Position;");
legend ("location", "northeast");

%figure(2);
%for m = measurements
%  m_pdf = normpdf(space, m, R);
%  plot(space, m_pdf, "r");
%  hold on;
%endfor;
  
  